-- ============================================================================
-- Karma Food App: Geräte-Freischaltung, Sperre nach Fehlversuchen, Sicherheits-Meldungen
-- Stand 24.11.2026 · Einspielen: Supabase → SQL Editor (EINMAL ausführen).
--
-- Was das macht
--  1. Ein neues Gerät muss einmalig freigeschaltet werden (Code oder Freigabe durch die Organisation).
--     Wer nur den Link hat, kommt nicht bis zur PIN-Abfrage.
--  2. 3 falsche PINs auf einem Gerät: dieses Gerät ist 5 Minuten gesperrt.
--  3. Die Organisation sieht Anfragen, Fehlversuche und gesperrte Geräte und kann (auch bei Dringlichkeit)
--     freigeben oder die Sperre aufheben.
--  4. Übergangszeit: Bis "grace_bis" (14 Tage ab Einspielen) funktioniert die alte Anmeldung ohne Gerät
--     weiter, damit niemand mitten im Betrieb ausgesperrt wird. Danach gilt nur noch die Freischaltung.
--
-- Was das NICHT ändert: Bestellungen, Mengen, Menü, Daten. Die PINs in "stores" bleiben, wie sie sind.
-- Der Datenzugriff über den öffentlichen Schlüssel ist damit noch NICHT geschützt (das ist Stufe 3).
--
-- Rückweg: ganz unten (Abschnitt ROLLBACK).
-- ============================================================================

begin;

-- ---------- Einstellungen (eine Zeile) ----------
create table if not exists public.sicherheit_einstellungen (
  id             int primary key default 1 check (id = 1),
  geraet_tage    int not null default 90,       -- so lange bleibt ein Gerät freigeschaltet
  versuche_max   int not null default 3,        -- falsche PINs bis zur Sperre
  sperre_minuten int not null default 5,        -- Dauer der Sperre
  grace_bis      timestamptz not null default (now() + interval '14 days')
);
insert into public.sicherheit_einstellungen (id) values (1) on conflict (id) do nothing;

-- ---------- Tabellen ----------
create table if not exists public.geraete (
  id               uuid primary key default gen_random_uuid(),
  token_hash       text not null unique,
  anfrage_code     text not null,
  status           text not null default 'wartet' check (status in ('wartet','freigegeben','abgelehnt','gesperrt')),
  bezeichnung      text,
  user_agent       text,
  erstellt_am      timestamptz not null default now(),
  freigegeben_am   timestamptz,
  freigegeben_von  text,
  gueltig_bis      timestamptz,
  gesperrt_bis     timestamptz,
  dringend_am      timestamptz,
  zuletzt_gesehen  timestamptz,
  letzte_filiale   text
);

create table if not exists public.geraete_codes (
  code         text primary key,
  erstellt_am  timestamptz not null default now(),
  gueltig_bis  timestamptz not null,
  eingeloest_am timestamptz,
  geraet_id    uuid
);

create table if not exists public.login_versuche (
  id          bigserial primary key,
  ts          timestamptz not null default now(),
  geraet_id   uuid,
  store_id    text,
  erfolg      boolean not null,
  grund       text,
  ip          text,
  user_agent  text,
  zaehlt      boolean not null default true,   -- false = zählt nicht mehr für die Sperre (nach Erfolg oder Aufhebung)
  quittiert   boolean not null default false   -- true = Organisation hat es gesehen
);
create index if not exists login_versuche_ts on public.login_versuche (ts desc);
create index if not exists login_versuche_geraet on public.login_versuche (geraet_id, ts desc);

create table if not exists public.admin_sitzungen (
  token_hash   text primary key,
  geraet_id    uuid,
  erstellt_am  timestamptz not null default now(),
  gueltig_bis  timestamptz not null
);

-- Die Tabellen sind für den öffentlichen Schlüssel komplett gesperrt (RLS an, keine Regeln).
-- Zugriff nur über die Funktionen unten.
alter table public.sicherheit_einstellungen enable row level security;
alter table public.geraete                  enable row level security;
alter table public.geraete_codes            enable row level security;
alter table public.login_versuche           enable row level security;
alter table public.admin_sitzungen          enable row level security;
revoke all on table public.sicherheit_einstellungen, public.geraete, public.geraete_codes,
                    public.login_versuche, public.admin_sitzungen from anon, authenticated;
revoke all on sequence public.login_versuche_id_seq from anon, authenticated;

-- ---------- Hilfsfunktionen (nicht von außen aufrufbar) ----------
create or replace function public.kf_hash(p text) returns text
language sql immutable as $$ select encode(sha256(convert_to(coalesce(p,''),'UTF8')),'hex') $$;

create or replace function public.kf_header(p_name text) returns text
language plpgsql stable as $$
declare h json;
begin
  begin h := current_setting('request.headers', true)::json; exception when others then return null; end;
  return h->>p_name;
end $$;

create or replace function public.kf_ip() returns text
language sql stable as $$ select nullif(trim(split_part(coalesce(public.kf_header('x-forwarded-for'), public.kf_header('cf-connecting-ip'), ''), ',', 1)), '') $$;

create or replace function public.kf_ua() returns text
language sql stable as $$ select left(public.kf_header('user-agent'), 200) $$;

create or replace function public.kf_status_text(g public.geraete) returns text
language sql stable as $$
  select case
    when g.status = 'freigegeben' and g.gueltig_bis is not null and g.gueltig_bis < now() then 'abgelaufen'
    when g.status in ('freigegeben','wartet') and g.gesperrt_bis is not null and g.gesperrt_bis > now() then 'gesperrt_zeit'
    else g.status end
$$;

create or replace function public.kf_admin(p_sitzung text) returns uuid
language plpgsql security definer set search_path = public as $$
declare v admin_sitzungen;
begin
  select * into v from admin_sitzungen where token_hash = kf_hash(p_sitzung) and gueltig_bis > now();
  if not found then raise exception 'nicht_berechtigt' using errcode = '42501'; end if;
  return coalesce(v.geraet_id, '00000000-0000-0000-0000-000000000000'::uuid);
end $$;

-- ---------- Gerät: Anfrage, Status, Code einlösen ----------
create or replace function public.geraet_anfordern(p_token text, p_ua text default null)
returns table(status text, anfrage_code text, gesperrt_sekunden int, gueltig_bis timestamptz, uebergang boolean)
language plpgsql security definer set search_path = public as $$
#variable_conflict use_column
declare g geraete; gb timestamptz;
begin
  select grace_bis into gb from sicherheit_einstellungen se where se.id = 1;
  if p_token is null or length(p_token) < 32 then raise exception 'token_ungueltig'; end if;
  select * into g from geraete where token_hash = kf_hash(p_token);
  if not found then
    insert into geraete (token_hash, anfrage_code, user_agent)
    values (kf_hash(p_token), upper(substr(replace(gen_random_uuid()::text,'-',''),1,4)), left(coalesce(p_ua, kf_ua()),200))
    returning * into g;
  end if;
  -- abgelaufene Freigabe: Gerät muss neu freigeschaltet werden (taucht dann wieder bei den Anfragen auf)
  if g.status = 'freigegeben' and g.gueltig_bis is not null and g.gueltig_bis < now() then
    update geraete set status = 'wartet', freigegeben_am = null, gueltig_bis = null,
           anfrage_code = upper(substr(replace(gen_random_uuid()::text,'-',''),1,4))
     where id = g.id returning * into g;
  end if;
  update geraete set zuletzt_gesehen = now() where id = g.id;
  return query select kf_status_text(g), g.anfrage_code,
    greatest(0, ceil(extract(epoch from (coalesce(g.gesperrt_bis, now()) - now()))))::int, g.gueltig_bis,
    (g.status = 'wartet' and now() < gb);
end $$;

create or replace function public.geraet_status(p_token text)
returns table(status text, anfrage_code text, gesperrt_sekunden int, gueltig_bis timestamptz, uebergang boolean)
language plpgsql security definer set search_path = public as $$
#variable_conflict use_column
declare g geraete; gb timestamptz;
begin
  select grace_bis into gb from sicherheit_einstellungen se where se.id = 1;
  select * into g from geraete where token_hash = kf_hash(p_token);
  if not found then
    return query select 'unbekannt'::text, null::text, 0, null::timestamptz, (now() < gb); return;
  end if;
  update geraete set zuletzt_gesehen = now() where id = g.id;
  return query select kf_status_text(g), g.anfrage_code,
    greatest(0, ceil(extract(epoch from (coalesce(g.gesperrt_bis, now()) - now()))))::int, g.gueltig_bis,
    (g.status = 'wartet' and now() < gb);
end $$;

-- Freischalt-Code einlösen (Code von der Organisation). Auch hier gilt die Sperre nach Fehlversuchen.
create or replace function public.geraet_code_einloesen(p_token text, p_code text)
returns text
language plpgsql security definer set search_path = public as $$
declare g geraete; c geraete_codes; e sicherheit_einstellungen; n int; k text;
begin
  select * into e from sicherheit_einstellungen se where se.id = 1;
  select * into g from geraete where token_hash = kf_hash(p_token);
  if not found then return 'geraet_unbekannt'; end if;
  if g.gesperrt_bis is not null and g.gesperrt_bis > now() then return 'gesperrt'; end if;
  if g.status = 'gesperrt' then return 'gesperrt_dauerhaft'; end if;
  k := upper(regexp_replace(coalesce(p_code,''), '[^A-Za-z0-9]', '', 'g'));
  select * into c from geraete_codes where code = k and eingeloest_am is null and gueltig_bis > now();
  if not found then
    insert into login_versuche (geraet_id, store_id, erfolg, grund, ip, user_agent)
    values (g.id, null, false, 'code_falsch', kf_ip(), kf_ua());
    select count(*) into n from login_versuche
      where geraet_id = g.id and erfolg = false and zaehlt and grund = 'code_falsch'
        and ts > now() - make_interval(mins => e.sperre_minuten);
    if n >= e.versuche_max then
      update geraete set gesperrt_bis = now() + make_interval(mins => e.sperre_minuten) where id = g.id;
      update login_versuche set zaehlt = false where geraet_id = g.id and grund = 'code_falsch';
      insert into login_versuche (geraet_id, erfolg, grund, ip, user_agent) values (g.id, false, 'sperre_ausgeloest', kf_ip(), kf_ua());
      return 'gesperrt';
    end if;
    return 'code_ungueltig';
  end if;
  update geraete_codes set eingeloest_am = now(), geraet_id = g.id where code = c.code;
  update geraete set status = 'freigegeben', freigegeben_am = now(), freigegeben_von = 'Code',
         gueltig_bis = now() + make_interval(days => e.geraet_tage), gesperrt_bis = null, dringend_am = null
   where id = g.id;
  return 'ok';
end $$;

-- Dringend: Gerät ist gesperrt oder wartet und meldet "bitte schnell freigeben"
create or replace function public.dringend_freigabe(p_token text)
returns text
language plpgsql security definer set search_path = public as $$
begin
  update geraete set dringend_am = now() where token_hash = kf_hash(p_token) and status <> 'abgelehnt';
  if not found then return 'geraet_unbekannt'; end if;
  insert into login_versuche (geraet_id, erfolg, grund, ip, user_agent)
    select id, false, 'dringend', kf_ip(), kf_ua() from geraete where token_hash = kf_hash(p_token);
  return 'ok';
end $$;

-- ---------- Anmeldung mit Filiale + PIN (neue Version, braucht ein freigeschaltetes Gerät) ----------
create or replace function public.kf_login(p_store_id text, p_pin text, p_token text)
returns table(status text, id text, name text, sekunden int, versuche_uebrig int, sitzung text)
language plpgsql security definer set search_path = public as $$
#variable_conflict use_column
declare g geraete; e sicherheit_einstellungen; s stores; n int; st text; sess text;
begin
  select * into e from sicherheit_einstellungen se where se.id = 1;
  select * into g from geraete where token_hash = kf_hash(p_token);
  if not found then
    return query select 'geraet_unbekannt'::text, null::text, null::text, 0, 0, null::text; return;
  end if;
  st := kf_status_text(g);
  if st = 'gesperrt_zeit' then
    return query select 'gesperrt'::text, null::text, null::text,
      greatest(1, ceil(extract(epoch from (g.gesperrt_bis - now()))))::int, 0, null::text; return;
  end if;
  if st = 'wartet' and now() < e.grace_bis then st := 'freigegeben'; end if;   -- Übergangszeit
  if st <> 'freigegeben' then
    return query select ('geraet_' || st)::text, null::text, null::text, 0, 0, null::text; return;
  end if;
  select * into s from stores where stores.id = p_store_id and stores.pin = p_pin;
  if found then
    update login_versuche set zaehlt = false where geraet_id = g.id and zaehlt;
    insert into login_versuche (geraet_id, store_id, erfolg, grund, ip, user_agent)
      values (g.id, p_store_id, true, 'ok', kf_ip(), kf_ua());
    update geraete set zuletzt_gesehen = now(), letzte_filiale = p_store_id where id = g.id;
    sess := null;
    if p_store_id = 'zentrale' then
      sess := replace(gen_random_uuid()::text,'-','') || replace(gen_random_uuid()::text,'-','');
      insert into admin_sitzungen (token_hash, geraet_id, gueltig_bis)
        values (kf_hash(sess), g.id, now() + interval '12 hours');
      delete from admin_sitzungen where gueltig_bis < now() - interval '1 day';
    end if;
    return query select 'ok'::text, s.id, s.name, 0, e.versuche_max, sess; return;
  end if;
  insert into login_versuche (geraet_id, store_id, erfolg, grund, ip, user_agent)
    values (g.id, p_store_id, false, 'pin_falsch', kf_ip(), kf_ua());
  select count(*) into n from login_versuche
    where geraet_id = g.id and erfolg = false and zaehlt and grund = 'pin_falsch'
      and ts > now() - make_interval(mins => e.sperre_minuten);
  if n >= e.versuche_max then
    update geraete set gesperrt_bis = now() + make_interval(mins => e.sperre_minuten) where id = g.id;
    update login_versuche set zaehlt = false where geraet_id = g.id and grund = 'pin_falsch' and zaehlt;
    insert into login_versuche (geraet_id, store_id, erfolg, grund, ip, user_agent)
      values (g.id, p_store_id, false, 'sperre_ausgeloest', kf_ip(), kf_ua());
    return query select 'gesperrt'::text, null::text, null::text, e.sperre_minuten * 60, 0, null::text; return;
  end if;
  return query select 'falsch'::text, null::text, null::text, 0, e.versuche_max - n, null::text;
end $$;

-- ---------- Alte Anmeldung: nur noch in der Übergangszeit ----------
-- Gleiche Signatur wie bisher, damit bereits geöffnete Apps weiterlaufen. Nach grace_bis liefert sie nichts mehr.
create or replace function public.check_store_pin(p_store_id text, p_pin text)
returns table(id text, name text)
language plpgsql security definer set search_path = public as $$
#variable_conflict use_column
declare e sicherheit_einstellungen; n int;
begin
  select * into e from sicherheit_einstellungen se where se.id = 1;
  if now() > e.grace_bis then return; end if;
  -- grobe Bremse für Altgeräte: höchstens 10 falsche Versuche je Filiale in der Sperrzeit
  select count(*) into n from login_versuche
    where geraet_id is null and store_id = p_store_id and erfolg = false and grund = 'pin_falsch_alt'
      and ts > now() - make_interval(mins => e.sperre_minuten);
  if n >= 10 then return; end if;
  if exists (select 1 from stores s where s.id = p_store_id and s.pin = p_pin) then
    insert into login_versuche (geraet_id, store_id, erfolg, grund, ip, user_agent, zaehlt)
      values (null, p_store_id, true, 'ok_alt', kf_ip(), kf_ua(), false);
    return query select s.id, s.name from stores s where s.id = p_store_id and s.pin = p_pin;
  else
    insert into login_versuche (geraet_id, store_id, erfolg, grund, ip, user_agent)
      values (null, p_store_id, false, 'pin_falsch_alt', kf_ip(), kf_ua());
  end if;
end $$;

-- ---------- Organisation: Übersicht, Freigabe, Sperre aufheben, Codes ----------
create or replace function public.sicherheit_uebersicht(p_sitzung text)
returns json
language plpgsql security definer set search_path = public as $$
declare r json;
begin
  perform kf_admin(p_sitzung);
  select json_build_object(
    'anfragen', coalesce((select json_agg(x order by x.dringend desc nulls last, x.erstellt_am) from (
        select id, anfrage_code as code, user_agent, erstellt_am, dringend_am as dringend from geraete where status = 'wartet') x), '[]'::json),
    'gesperrt', coalesce((select json_agg(x order by x.dringend desc nulls last) from (
        select id, bezeichnung, anfrage_code as code, user_agent, letzte_filiale, dringend_am as dringend, gesperrt_bis, status
        from geraete where status = 'gesperrt' or (gesperrt_bis is not null and gesperrt_bis > now())) x), '[]'::json),
    'geraete', coalesce((select json_agg(x order by x.zuletzt desc nulls last) from (
        select id, bezeichnung, anfrage_code as code, user_agent, freigegeben_am, freigegeben_von, gueltig_bis,
               zuletzt_gesehen as zuletzt, letzte_filiale, status
        from geraete where status = 'freigegeben' limit 200) x), '[]'::json),
    'versuche', coalesce((select json_agg(x order by x.ts desc) from (
        select v.ts, v.store_id, v.grund, v.ip, v.user_agent, v.quittiert, g.anfrage_code as code, g.bezeichnung
        from login_versuche v left join geraete g on g.id = v.geraet_id
        where v.erfolg = false and v.ts > now() - interval '7 days' order by v.ts desc limit 60) x), '[]'::json),
    'neu', (select count(*) from login_versuche where erfolg = false and not quittiert and ts > now() - interval '7 days'),
    'codes', coalesce((select json_agg(x order by x.gueltig_bis desc) from (
        select code, gueltig_bis from geraete_codes where eingeloest_am is null and gueltig_bis > now()) x), '[]'::json),
    'jetzt', now()
  ) into r;
  return r;
end $$;

create or replace function public.geraet_freigeben(p_sitzung text, p_id uuid, p_bezeichnung text default null)
returns text
language plpgsql security definer set search_path = public as $$
declare e sicherheit_einstellungen; n int;
begin
  perform kf_admin(p_sitzung);
  select * into e from sicherheit_einstellungen se where se.id = 1;
  update geraete set status = 'freigegeben', freigegeben_am = now(), freigegeben_von = 'Organisation',
         gueltig_bis = now() + make_interval(days => e.geraet_tage), gesperrt_bis = null, dringend_am = null,
         bezeichnung = coalesce(nullif(trim(p_bezeichnung),''), bezeichnung)
   where id = p_id;
  get diagnostics n = row_count;
  update login_versuche set zaehlt = false where geraet_id = p_id and zaehlt;
  return case when n > 0 then 'ok' else 'nicht_gefunden' end;
end $$;

create or replace function public.sperre_aufheben(p_sitzung text, p_id uuid)
returns text
language plpgsql security definer set search_path = public as $$
declare n int;
begin
  perform kf_admin(p_sitzung);
  update geraete set gesperrt_bis = null, dringend_am = null where id = p_id;
  get diagnostics n = row_count;
  update login_versuche set zaehlt = false where geraet_id = p_id and zaehlt;
  return case when n > 0 then 'ok' else 'nicht_gefunden' end;
end $$;

create or replace function public.geraet_ablehnen(p_sitzung text, p_id uuid)
returns text
language plpgsql security definer set search_path = public as $$
begin
  perform kf_admin(p_sitzung);
  update geraete set status = 'abgelehnt', dringend_am = null where id = p_id;
  return case when found then 'ok' else 'nicht_gefunden' end;
end $$;

create or replace function public.geraet_sperren(p_sitzung text, p_id uuid)
returns text
language plpgsql security definer set search_path = public as $$
begin
  perform kf_admin(p_sitzung);
  update geraete set status = 'gesperrt' where id = p_id;
  return case when found then 'ok' else 'nicht_gefunden' end;
end $$;

create or replace function public.geraet_entfernen(p_sitzung text, p_id uuid)
returns text
language plpgsql security definer set search_path = public as $$
begin
  perform kf_admin(p_sitzung);
  delete from geraete where id = p_id;
  return case when found then 'ok' else 'nicht_gefunden' end;
end $$;

create or replace function public.geraet_umbenennen(p_sitzung text, p_id uuid, p_bezeichnung text)
returns text
language plpgsql security definer set search_path = public as $$
begin
  perform kf_admin(p_sitzung);
  update geraete set bezeichnung = left(nullif(trim(p_bezeichnung),''), 60) where id = p_id;
  return case when found then 'ok' else 'nicht_gefunden' end;
end $$;

create or replace function public.code_erzeugen(p_sitzung text)
returns table(code text, gueltig_bis timestamptz)
language plpgsql security definer set search_path = public as $$
#variable_conflict use_column
declare k text; t timestamptz;
begin
  perform kf_admin(p_sitzung);
  k := upper(substr(replace(gen_random_uuid()::text,'-',''),1,8));
  t := now() + interval '24 hours';
  insert into geraete_codes (code, gueltig_bis) values (k, t);
  delete from geraete_codes where gueltig_bis < now() - interval '7 days';
  return query select k, t;
end $$;

create or replace function public.fehlversuche_quittieren(p_sitzung text)
returns text
language plpgsql security definer set search_path = public as $$
begin
  perform kf_admin(p_sitzung);
  update login_versuche set quittiert = true where not quittiert;
  return 'ok';
end $$;

-- ---------- Rechte: nur die gewollten Funktionen sind von außen aufrufbar ----------
revoke all on function public.kf_hash(text), public.kf_header(text), public.kf_ip(), public.kf_ua(),
                       public.kf_status_text(public.geraete), public.kf_admin(text) from public, anon, authenticated;
grant execute on function
  public.geraet_anfordern(text,text), public.geraet_status(text), public.geraet_code_einloesen(text,text),
  public.dringend_freigabe(text), public.kf_login(text,text,text), public.check_store_pin(text,text),
  public.sicherheit_uebersicht(text), public.geraet_freigeben(text,uuid,text), public.sperre_aufheben(text,uuid),
  public.geraet_ablehnen(text,uuid), public.geraet_sperren(text,uuid), public.geraet_entfernen(text,uuid),
  public.geraet_umbenennen(text,uuid,text), public.code_erzeugen(text), public.fehlversuche_quittieren(text)
to anon, authenticated;

commit;

-- ============================================================================
-- OPTIONAL (einzeln ausführen, NICHT Teil des Skripts oben):
-- Neue, nicht erratbare PINs für alle Filialen. Das Ergebnis erscheint nur hier im Editor,
-- bitte notieren und an die Teams geben. 1070 (geschlossen) bleibt unberührt.
--   update public.stores set pin = lpad((floor(random()*10000))::int::text, 4, '0')
--   where id <> '1070' returning id, name, pin;
--
-- Ersten Freischalt-Code erzeugen (z. B. für dein eigenes Gerät, falls die Übergangszeit schon vorbei ist):
--   insert into public.geraete_codes (code, gueltig_bis)
--   values (upper(substr(replace(gen_random_uuid()::text,'-',''),1,8)), now() + interval '24 hours') returning code;
--
-- Übergangszeit verlängern oder beenden:
--   update public.sicherheit_einstellungen set grace_bis = now() + interval '7 days' where id = 1;
--   update public.sicherheit_einstellungen set grace_bis = now() where id = 1;   -- sofort beenden
-- ============================================================================

-- ============================================================================
-- ROLLBACK (alles zurück auf den Stand vorher; die alte Anmeldung funktioniert dann wieder ohne Gerät)
-- begin;
--   create or replace function public.check_store_pin(p_store_id text, p_pin text)
--     returns table(id text, name text) language sql security definer set search_path to 'public'
--     as $f$ select s.id, s.name from public.stores s where s.id = p_store_id and s.pin = p_pin; $f$;
--   drop function if exists public.kf_login(text,text,text), public.geraet_anfordern(text,text), public.geraet_status(text),
--     public.geraet_code_einloesen(text,text), public.dringend_freigabe(text), public.sicherheit_uebersicht(text),
--     public.geraet_freigeben(text,uuid,text), public.sperre_aufheben(text,uuid), public.geraet_ablehnen(text,uuid),
--     public.geraet_sperren(text,uuid), public.geraet_entfernen(text,uuid), public.geraet_umbenennen(text,uuid,text),
--     public.code_erzeugen(text), public.fehlversuche_quittieren(text), public.kf_admin(text);
--   drop function if exists public.kf_status_text(public.geraete), public.kf_ua(), public.kf_ip(),
--     public.kf_header(text), public.kf_hash(text);
--   drop table if exists public.admin_sitzungen, public.login_versuche, public.geraete_codes, public.geraete,
--     public.sicherheit_einstellungen;
-- commit;
-- ============================================================================

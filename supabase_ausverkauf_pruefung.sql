-- Ausverkauf prüfen (Report, Organisation): wie viele Gerichte waren 30 Min. vor Schluss noch da (0 bis 3)?
create table if not exists public.ausverkauf_pruefung (
  store_id text not null,
  datum date not null,
  gerichte_verfuegbar int not null check (gerichte_verfuegbar between 0 and 3),
  created_at timestamptz not null default now(),
  primary key (store_id, datum)
);
alter table public.ausverkauf_pruefung enable row level security;
drop policy if exists ausverkauf_pruefung_app on public.ausverkauf_pruefung;
create policy ausverkauf_pruefung_app on public.ausverkauf_pruefung for all to anon, authenticated using (true) with check (true);

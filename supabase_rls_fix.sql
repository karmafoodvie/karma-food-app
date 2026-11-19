-- RLS für die 7 Tabellen ohne Row Level Security (Supabase-Advisor: critical)
-- Stand: 03.11.26 – NOCH NICHT ANGEWENDET. Vorher prüfen, dann im SQL Editor ausführen
-- (oder per Supabase-MCP apply_migration). In einer Transaktion, damit alles oder nichts greift.
--
-- Grundlage: Die App nutzt für alles den Anon-Key (Login nur über Filial-PIN, kein Supabase Auth).
-- Die Policies erlauben deshalb nur genau die Verben, die public/index.html pro Tabelle benutzt –
-- alles andere (z. B. UPDATE/DELETE auf page_views) ist danach gesperrt. Das ist Schadensbegrenzung,
-- KEIN Ersatz für echte Authentifizierung: wer den Anon-Key kennt, kann weiterhin die erlaubten
-- Verben ausführen. Gleiches Muster wie bei den übrigen Tabellen (orders, samosa_today, …).
--
-- Rollback: ALTER TABLE public.<tabelle> DISABLE ROW LEVEL SECURITY;

begin;

-- freitag_checkliste: SELECT, INSERT, DELETE (Zeile ~8454–8483)
alter table public.freitag_checkliste enable row level security;
create policy freitag_checkliste_select on public.freitag_checkliste for select using (true);
create policy freitag_checkliste_insert on public.freitag_checkliste for insert with check (true);
create policy freitag_checkliste_delete on public.freitag_checkliste for delete using (true);

-- samosa_lock: SELECT, INSERT (Zeile ~17564–17766)
alter table public.samosa_lock enable row level security;
create policy samosa_lock_select on public.samosa_lock for select using (true);
create policy samosa_lock_insert on public.samosa_lock for insert with check (true);

-- rabatt_codes: voller CRUD (Orga-Verwaltung ~847–942, Lesen in Hilfe ~1353)
alter table public.rabatt_codes enable row level security;
create policy rabatt_codes_select on public.rabatt_codes for select using (true);
create policy rabatt_codes_insert on public.rabatt_codes for insert with check (true);
create policy rabatt_codes_update on public.rabatt_codes for update using (true) with check (true);
create policy rabatt_codes_delete on public.rabatt_codes for delete using (true);

-- wochen_erkenntnisse: SELECT, INSERT (Zeile ~20501, 20626)
alter table public.wochen_erkenntnisse enable row level security;
create policy wochen_erkenntnisse_select on public.wochen_erkenntnisse for select using (true);
create policy wochen_erkenntnisse_insert on public.wochen_erkenntnisse for insert with check (true);

-- page_views: INSERT (Tracking ~2322) und SELECT (Nutzungsstatistik ~9062). Kein UPDATE/DELETE.
alter table public.page_views enable row level security;
create policy page_views_select on public.page_views for select using (true);
create policy page_views_insert on public.page_views for insert with check (true);

-- essen_notruf: SELECT, INSERT, UPDATE (Zeile ~4313–4514). Kein DELETE (Erledigt-Flag statt Löschen).
alter table public.essen_notruf enable row level security;
create policy essen_notruf_select on public.essen_notruf for select using (true);
create policy essen_notruf_insert on public.essen_notruf for insert with check (true);
create policy essen_notruf_update on public.essen_notruf for update using (true) with check (true);

-- tg_artikel: voller CRUD (Zeile ~10051–10296)
alter table public.tg_artikel enable row level security;
create policy tg_artikel_select on public.tg_artikel for select using (true);
create policy tg_artikel_insert on public.tg_artikel for insert with check (true);
create policy tg_artikel_update on public.tg_artikel for update using (true) with check (true);
create policy tg_artikel_delete on public.tg_artikel for delete using (true);

commit;

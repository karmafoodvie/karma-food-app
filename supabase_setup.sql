-- ============================================
-- KARMA FOOD BESTELLSYSTEM -- Supabase Setup
-- Einmal ausführen im Supabase SQL Editor
-- ============================================

-- 1. STORES
create table if not exists stores (
  id text primary key,
  name text not null,
  pin text not null
);

insert into stores (id, name, pin) values
  ('1070', '1070 Wien', '1070'),
  ('1020', '1020 Wien', '1020'),
  ('boerse', 'Börse', '2626'),
  ('3400', '3400 Klosterneuburg', '3400'),
  ('kloster2', 'Klosterneuburg 2', '4400'),
  ('lb', 'LB Laurenzerberg', '5500'),
  ('zentrale', 'Zentrale / Transporter', '9999')
on conflict do nothing;

-- 2. ARTIKEL STAMMLISTE
create table if not exists articles (
  id serial primary key,
  category text not null,
  name text not null,
  unit text not null,
  min_stock integer default 4,
  sort_order integer default 0
);

insert into articles (category, name, unit, min_stock, sort_order) values
  ('Verpackungen','Curry Boxen','Pkg',4,1),
  ('Verpackungen','Curry Deckel','Pkg',4,2),
  ('Verpackungen','Dal Becher','Pkg',4,3),
  ('Verpackungen','Dal Deckel','Pkg',4,4),
  ('Verpackungen','Papiertragetaschen/Sackerl','Pkg',4,5),
  ('Verpackungen','Servietten','Pkg',6,6),
  ('Verpackungen','Papiersackerl (Sweets)','Pkg',2,7),
  ('Verpackungen','Pappteller (Sweets)','Pkg',2,8),
  ('Verpackungen','Kaffeebecher & Deckel gross','Pkg',4,9),
  ('Verpackungen','Kaffeebecher & Deckel klein','Pkg',4,10),
  ('Verpackungen','Löffel (Holz)','Pkg',4,11),
  ('Verpackungen','Gabeln (Holz)','Pkg',4,12),
  ('Alltag','Bonrollen Kreditkartengerät','Pkg á 3',2,13),
  ('Alltag','Rechnungsdrucker Rollen','Pkg á 3',2,14),
  ('Alltag','Geschirrtücher','Stk',4,15),
  ('Alltag','Mikrofasertuch','Stk',4,16),
  ('Alltag','Müllsäcke klein','Pkg',2,17),
  ('Alltag','Müllsäcke groß','Pkg',2,18),
  ('Alltag','Küchenrolle','Stk',4,19),
  ('Alltag','Bürste Abwasch','Stk',2,20),
  ('Alltag','Drahtschwamm','Stk',2,21),
  ('Alltag','Stempelkarte Lunch','Stk',10,22),
  ('Alltag','Stempelkarte Kaffee','Stk',10,23),
  ('Food & Drinks','Chiliflocken','Stk',4,24),
  ('Food & Drinks','Chaisirup Groß','Stk',2,25),
  ('Food & Drinks','PONA','Stk',6,26),
  ('Food & Drinks','Mango Lassi','Stk',6,27),
  ('Food & Drinks','Kuhmilch','Stk',6,28),
  ('Food & Drinks','Hafermilch','Stk',6,29),
  ('Food & Drinks','Mineral prickelnd','Stk',6,30),
  ('Food & Drinks','Bareballs White Almond','Stk',4,31),
  ('Food & Drinks','Bareballs Peanut','Stk',4,32),
  ('Reinigung','Geschirrspülermittel Kanister','Stk',2,33),
  ('Reinigung','Glanzklarmittel Kanister','Stk',2,34),
  ('Reinigung','Handspülmittel','Stk',2,35),
  ('Reinigung','Küchenreiniger (Oberflächen)','Stk',2,36),
  ('Reinigung','Glasreiniger','Stk',2,37),
  ('Reinigung','Parkett-/Laminatpflege','Stk',1,38),
  ('Reinigung','Boden Kraft Reiniger','Stk',1,39),
  ('Reinigung','WC Spezial Reiniger','Stk',2,40)
on conflict do nothing;

-- 3. TÄGLICHE BESTELLUNGEN
create table if not exists orders (
  id serial primary key,
  store_id text references stores(id),
  article_id integer references articles(id),
  quantity integer not null default 0,
  order_date date not null default current_date,
  created_at timestamptz default now(),
  unique(store_id, article_id, order_date)
);

-- 4. LAGERBESTAND
create table if not exists stock (
  article_id integer primary key references articles(id),
  quantity integer not null default 0,
  updated_at timestamptz default now()
);

insert into stock (article_id, quantity)
select id, 8 from articles
on conflict do nothing;

-- 5. CHECKLISTEN VORLAGEN
create table if not exists checklist_templates (
  id serial primary key,
  list_type text not null,  -- 'oeffnung', 'reinigung', 'abschluss'
  section text not null,
  item_text text not null,
  sort_order integer default 0
);

insert into checklist_templates (list_type, section, item_text, sort_order) values
  ('oeffnung','Vor dem Öffnen','Eingang & Schaufenster reinigen',1),
  ('oeffnung','Vor dem Öffnen','Kühlschrank Temperatur prüfen',2),
  ('oeffnung','Vor dem Öffnen','Kassensystem starten & testen',3),
  ('oeffnung','Aufbau','Speisen aus Kühlung nehmen',4),
  ('oeffnung','Aufbau','Verpackungen auffüllen',5),
  ('oeffnung','Aufbau','Wechselgeld prüfen',6),
  ('reinigung','Flächen','Tresen & Ausgabe desinfizieren',1),
  ('reinigung','Flächen','Böden kehren',2),
  ('reinigung','Flächen','Böden wischen',3),
  ('reinigung','Flächen','Kühlschrank außen reinigen',4),
  ('reinigung','Geräte','Kaffeemaschine reinigen',5),
  ('reinigung','Geräte','Geschirrspüler leeren & einräumen',6),
  ('reinigung','Geräte','Mikrowelle reinigen',7),
  ('abschluss','Kasse & Abrechnung','Tagesabschluss Kasse machen',1),
  ('abschluss','Kasse & Abrechnung','Wechselgeld für morgen richten',2),
  ('abschluss','Kasse & Abrechnung','Tageseinnahmen notieren',3),
  ('abschluss','Sicherheit','Alle Geräte ausschalten',4),
  ('abschluss','Sicherheit','Kühlschrank Temperatur final prüfen',5),
  ('abschluss','Sicherheit','Türen & Fenster sperren',6)
on conflict do nothing;

-- 6. ERLEDIGTE CHECKLISTENPUNKTE (täglich)
create table if not exists checklist_done (
  id serial primary key,
  store_id text references stores(id),
  template_id integer references checklist_templates(id),
  done_date date not null default current_date,
  done_at timestamptz default now(),
  unique(store_id, template_id, done_date)
);

-- 7. ROW LEVEL SECURITY (empfohlen)
alter table orders enable row level security;
alter table stock enable row level security;
alter table checklist_done enable row level security;

-- Öffentlicher Lesezugriff (da wir PIN-Auth verwenden)
create policy "public read orders" on orders for select using (true);
create policy "public insert orders" on orders for insert with check (true);
create policy "public update orders" on orders for update using (true);
create policy "public read stock" on stock for select using (true);
create policy "public update stock" on stock for update using (true);
create policy "public read checklist_done" on checklist_done for select using (true);
create policy "public insert checklist_done" on checklist_done for insert with check (true);
create policy "public delete checklist_done" on checklist_done for delete using (true);
create policy "public read articles" on articles for select using (true);
create policy "public read stores" on stores for select using (true);
create policy "public read templates" on checklist_templates for select using (true);

alter table articles enable row level security;
alter table stores enable row level security;
alter table checklist_templates enable row level security;

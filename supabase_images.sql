-- Image URL Spalten hinzufügen
ALTER TABLE stores ADD COLUMN IF NOT EXISTS image_url text;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS image_url text;

-- Storage Bucket Policy (nachdem du den Bucket "images" erstellt hast)
CREATE POLICY "Public read images" ON storage.objects
  FOR SELECT USING (bucket_id = 'images');

CREATE POLICY "Auth upload images" ON storage.objects
  FOR INSERT WITH CHECK (bucket_id = 'images');

-- Tabelle für Sonderbestellungen
CREATE TABLE IF NOT EXISTS special_orders (
  id serial primary key,
  store_id text references stores(id),
  note text not null,
  order_date date not null default current_date,
  created_at timestamptz default now(),
  unique(store_id, order_date)
);
alter table special_orders enable row level security;
create policy "public read special" on special_orders for select using (true);
create policy "public insert special" on special_orders for insert with check (true);
create policy "public update special" on special_orders for update using (true);
create policy "public delete special" on special_orders for delete using (true);

-- Stores neu befüllen
DELETE FROM stores;
INSERT INTO stores (id, name, pin) VALUES
  ('lb',       'Laurenzerberg 1010',        '5500'),
  ('boerse',   'Börse 1010',                '2626'),
  ('1020',     'Ausstellungsstraße 1020',   '1020'),
  ('1070',     'Neustiftgasse 1070',        '1070'),
  ('3400',     'Stadtplatz 3400',           '3400'),
  ('kitchen',  'Kitchen 3400',              '3401'),
  ('zentrale', 'Zentrale / Transporter',    '9999');

-- Reinigungsmittel als eigene Kategorie (für Casey/KC)
-- Die sind bereits als "Reinigung" in der DB, nur umbenennen falls nötig

-- KC/Webshop Produkte hinzufügen
INSERT INTO articles (category, name, unit, min_stock, sort_order) VALUES
  ('Webshop-Produkte','Kashmiri Chili Crisp','Stk',3,50),
  ('Webshop-Produkte','Korma Paste','Stk',8,51),
  ('Webshop-Produkte','Curry Paste','Stk',8,52),
  ('Webshop-Produkte','Madras Paste','Stk',8,53),
  ('Webshop-Produkte','Masala Trio - Starter','Stk',2,54),
  ('Webshop-Produkte','Masala Trio - Adventure','Stk',2,55),
  ('Webshop-Produkte','Mama Masala','Stk',5,56),
  ('Webshop-Produkte','Papa Masala','Stk',5,57),
  ('Webshop-Produkte','Dal Masala','Stk',5,58),
  ('Webshop-Produkte','Golden Salt','Stk',5,59),
  ('Webshop-Produkte','Goa Masala','Stk',5,60),
  ('Webshop-Produkte','BBQ Masala','Stk',5,61),
  ('Webshop-Produkte','Chai Masala','Stk',5,62),
  ('Webshop-Produkte','Mango Chilli Sauce','Stk',3,63),
  ('Webshop-Produkte','Chai Sirup','Stk',3,64),
  ('Webshop-Produkte','KARMA LUNCH CLUB BAG','Stk',10,65),
  ('Webshop-Produkte','Kochbuch alt','Stk',3,66),
  ('Webshop-Produkte','Kochbuch Curry','Stk',3,67),
  ('Webshop-Produkte','Weducer Cup','Stk',2,68)
ON CONFLICT DO NOTHING;

-- Sweets Produkte hinzufügen
INSERT INTO articles (category, name, unit, min_stock, sort_order) VALUES
  ('Sweets','Tahini Bananen Muffin','Stk',2,70),
  ('Sweets','Raw Cake Chocolate','Stk',1,71),
  ('Sweets','Raw Cake Passion Fruit','Stk',1,72),
  ('Sweets','Choco Coconut Cake','Stk',1,73)
ON CONFLICT DO NOTHING;

-- Tabelle für IST-Bestand der KC-Produkte (pro Filiale)
CREATE TABLE IF NOT EXISTS kc_stock (
  id serial primary key,
  store_id text references stores(id),
  article_id integer references articles(id),
  ist_bestand numeric not null,
  updated_date date not null default current_date,
  created_at timestamptz default now(),
  unique(store_id, article_id)
);
alter table kc_stock enable row level security;
create policy "public read kc_stock" on kc_stock for select using (true);
create policy "public insert kc_stock" on kc_stock for insert with check (true);
create policy "public update kc_stock" on kc_stock for update using (true);
create policy "public delete kc_stock" on kc_stock for delete using (true);

-- SOLL-Bestand (min_stock) gemäß echtem Google Sheet aktualisieren
UPDATE articles SET min_stock = 3 WHERE name = 'Kashmiri Chili Crisp';
UPDATE articles SET min_stock = 8 WHERE name = 'Korma Paste';
UPDATE articles SET min_stock = 8 WHERE name = 'Curry Paste';
UPDATE articles SET min_stock = 8 WHERE name = 'Madras Paste';
UPDATE articles SET min_stock = 2 WHERE name = 'Masala Trio - Starter';
UPDATE articles SET min_stock = 2 WHERE name = 'Masala Trio - Adventure';
UPDATE articles SET min_stock = 5 WHERE name = 'Mama Masala';
UPDATE articles SET min_stock = 5 WHERE name = 'Papa Masala';
UPDATE articles SET min_stock = 5 WHERE name = 'Dal Masala';
UPDATE articles SET min_stock = 5 WHERE name = 'Golden Salt';
UPDATE articles SET min_stock = 5 WHERE name = 'Goa Masala';
UPDATE articles SET min_stock = 5 WHERE name = 'BBQ Masala';
UPDATE articles SET min_stock = 5 WHERE name = 'Chai Masala';
UPDATE articles SET min_stock = 3 WHERE name = 'Mango Chilli Sauce';
UPDATE articles SET min_stock = 3 WHERE name = 'Chai Sirup';
UPDATE articles SET min_stock = 10 WHERE name = 'KARMA LUNCH CLUB BAG';
UPDATE articles SET min_stock = 3 WHERE name = 'Kochbuch alt';
UPDATE articles SET min_stock = 3 WHERE name = 'Kochbuch Curry';
UPDATE articles SET min_stock = 2 WHERE name = 'Weducer Cup';

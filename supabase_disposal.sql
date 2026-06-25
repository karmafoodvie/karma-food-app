-- Wochenplan: welches Gericht läuft an welchem Wochentag in welchem Slot
CREATE TABLE IF NOT EXISTS weekly_menu (
  id serial primary key,
  weekday text not null, -- 'mo','di','mi','do','fr'
  slot text not null,    -- 'salat','gericht1','gericht2','gericht3','reis'
  dish_name text not null default '',
  updated_at timestamptz default now(),
  unique(weekday, slot)
);
alter table weekly_menu enable row level security;
create policy "public read weekly_menu" on weekly_menu for select using (true);
create policy "public insert weekly_menu" on weekly_menu for insert with check (true);
create policy "public update weekly_menu" on weekly_menu for update using (true);
create policy "public delete weekly_menu" on weekly_menu for delete using (true);

-- Entsorgung: pro Filiale, Tag, Slot -> Menge (Restmenge) + Uhrzeit (ausverkauft/entsorgt) + Notiz
CREATE TABLE IF NOT EXISTS disposal (
  id serial primary key,
  store_id text references stores(id),
  disposal_date date not null default current_date,
  slot text not null, -- 'salat','gericht1','gericht2','gericht3','reis'
  dish_name text,      -- snapshot of dish name at time of entry, for historical accuracy
  sold_out_time time,  -- wann ausverkauft
  leftover_qty numeric, -- Restmenge am Ende
  note text,
  updated_at timestamptz default now(),
  unique(store_id, disposal_date, slot)
);
alter table disposal enable row level security;
create policy "public read disposal" on disposal for select using (true);
create policy "public insert disposal" on disposal for insert with check (true);
create policy "public update disposal" on disposal for update using (true);
create policy "public delete disposal" on disposal for delete using (true);

-- Initialer Wochenplan basierend auf dem Google Sheet Muster
INSERT INTO weekly_menu (weekday, slot, dish_name) VALUES
  ('mo','salat','Salat'),('mo','gericht1','Curry'),('mo','gericht2','Bowl'),('mo','gericht3','Dal'),('mo','reis','Reis'),
  ('di','salat','Salat'),('di','gericht1','Curry'),('di','gericht2','Lasagne'),('di','gericht3','Dal'),('di','reis','Reis'),
  ('mi','salat','Salat'),('mi','gericht1','Curry'),('mi','gericht2','Biryani'),('mi','gericht3','Special'),('mi','reis','Reis'),
  ('do','salat','Salat'),('do','gericht1','Curry'),('do','gericht2','Lasagne'),('do','gericht3','Dal'),('do','reis','Reis'),
  ('fr','salat','Salat'),('fr','gericht1','Curry'),('fr','gericht2','Biryani'),('fr','gericht3','Dal'),('fr','reis','Reis')
ON CONFLICT (weekday, slot) DO NOTHING;

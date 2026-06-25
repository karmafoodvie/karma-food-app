-- ============================================================
-- KÜCHE-BESTELLUNG (Bowl Sauce, Limetten, Dressing, Petersilie, Salat, Raita)
-- Fixe Grundmengen pro Filiale & Wochentag, mit Anpassungsmöglichkeit
-- ============================================================

-- 1) Grundmengen (die "Soll-Liste" aus dem Auslieferplan-Foto)
CREATE TABLE IF NOT EXISTS kitchen_supply_baseline (
  id SERIAL PRIMARY KEY,
  store_id TEXT NOT NULL REFERENCES stores(id),
  weekday INT NOT NULL,              -- 1=Montag ... 5=Freitag
  article_name TEXT NOT NULL,        -- 'Bowl Sauce','Limetten','Dressing','Petersilie','Salat','Raita'
  unit TEXT NOT NULL,                -- 'Becher','GN','Stk'
  base_qty NUMERIC NOT NULL,         -- z.B. 1, 1.5, 0.75 (3/4), 0.333 (1/3)
  UNIQUE(store_id, weekday, article_name)
);

-- 2) Tagesaktuelle Werte (Grundmenge ODER manuell angepasst)
CREATE TABLE IF NOT EXISTS kitchen_supply_today (
  id SERIAL PRIMARY KEY,
  store_id TEXT NOT NULL REFERENCES stores(id),
  supply_date DATE NOT NULL,
  article_name TEXT NOT NULL,
  qty NUMERIC NOT NULL,
  is_adjusted BOOLEAN DEFAULT FALSE,  -- true = manuell abweichend von Grundmenge
  changed_by TEXT,                    -- z.B. Filialname/PIN-Kontext
  changed_at TIMESTAMPTZ,
  kitchen_notified BOOLEAN DEFAULT FALSE,
  UNIQUE(store_id, supply_date, article_name)
);

ALTER TABLE kitchen_supply_baseline ENABLE ROW LEVEL SECURITY;
ALTER TABLE kitchen_supply_today ENABLE ROW LEVEL SECURITY;

CREATE POLICY "public read baseline" ON kitchen_supply_baseline FOR SELECT USING (true);
CREATE POLICY "public write baseline" ON kitchen_supply_baseline FOR ALL USING (true);
CREATE POLICY "public read today" ON kitchen_supply_today FOR SELECT USING (true);
CREATE POLICY "public write today" ON kitchen_supply_today FOR ALL USING (true);

-- ============================================================
-- GRUNDDATEN (aus Auslieferplan-Foto, Stadtplatz korrigiert: 15 Limetten / 1.5 Petersilie Mo)
-- Wochentag: 1=Mo, 2=Di, 3=Mi, 4=Do, 5=Fr
-- ============================================================

INSERT INTO kitchen_supply_baseline (store_id, weekday, article_name, unit, base_qty) VALUES
-- MONTAG
('boerse', 1, 'Bowl Sauce', 'Becher', 1),
('lb',     1, 'Bowl Sauce', 'Becher', 1),
('1020',   1, 'Bowl Sauce', 'Becher', 0.75),
('1070',   1, 'Bowl Sauce', 'Becher', 0.5),
('3400',   1, 'Bowl Sauce', 'Becher', 1),

('boerse', 1, 'Limetten', 'Stk', 25),
('lb',     1, 'Limetten', 'Stk', 30),
('1020',   1, 'Limetten', 'Stk', 25),
('1070',   1, 'Limetten', 'Stk', 20),
('3400',   1, 'Limetten', 'Stk', 15),

('boerse', 1, 'Dressing', 'Becher', 1.5),
('lb',     1, 'Dressing', 'Becher', 1.5),
('1020',   1, 'Dressing', 'Becher', 1.5),
('1070',   1, 'Dressing', 'Becher', 0.5),
('3400',   1, 'Dressing', 'Becher', 1.5),

('boerse', 1, 'Petersilie', 'Becher', 0.5),
('lb',     1, 'Petersilie', 'Becher', 0.5),
('1020',   1, 'Petersilie', 'Becher', 0.5),
('1070',   1, 'Petersilie', 'Becher', 0.333),
('3400',   1, 'Petersilie', 'Becher', 1.5),

('3400',   1, 'Salat', 'GN', 0.75),

-- DIENSTAG
('boerse', 2, 'Salat', 'GN', 1.5),
('lb',     2, 'Salat', 'GN', 1.5),
('1020',   2, 'Salat', 'GN', 0.75),
('1070',   2, 'Salat', 'GN', 0.75),
('3400',   2, 'Salat', 'GN', 1.5),

('boerse', 2, 'Petersilie', 'Becher', 0.5),
('lb',     2, 'Petersilie', 'Becher', 0.5),
('1020',   2, 'Petersilie', 'Becher', 0.5),
('1070',   2, 'Petersilie', 'Becher', 0.333),

-- MITTWOCH
('boerse', 3, 'Raita', 'Becher', 1.5),
('lb',     3, 'Raita', 'Becher', 1.5),
('1020',   3, 'Raita', 'Becher', 1),
('1070',   3, 'Raita', 'Becher', 0.75),
('3400',   3, 'Raita', 'Becher', 1),

('3400',   3, 'Salat', 'GN', 0.75),

('boerse', 3, 'Petersilie', 'Becher', 0.5),
('lb',     3, 'Petersilie', 'Becher', 0.5),
('1020',   3, 'Petersilie', 'Becher', 0.5),
('1070',   3, 'Petersilie', 'Becher', 0.333),

-- DONNERSTAG
('boerse', 4, 'Salat', 'GN', 1.5),
('lb',     4, 'Salat', 'GN', 1.5),
('1020',   4, 'Salat', 'GN', 0.75),
('1070',   4, 'Salat', 'GN', 0.75),
('3400',   4, 'Salat', 'GN', 1.5),

('boerse', 4, 'Petersilie', 'Becher', 0.5),
('lb',     4, 'Petersilie', 'Becher', 0.5),
('1020',   4, 'Petersilie', 'Becher', 0.5),
('1070',   4, 'Petersilie', 'Becher', 0.333),

-- FREITAG
('boerse', 5, 'Raita', 'Becher', 1.5),
('lb',     5, 'Raita', 'Becher', 1.5),
('1020',   5, 'Raita', 'Becher', 1),
('1070',   5, 'Raita', 'Becher', 0.75),
('3400',   5, 'Raita', 'Becher', 1),

('3400',   5, 'Salat', 'GN', 0.75),

('boerse', 5, 'Petersilie', 'Becher', 0.5),
('lb',     5, 'Petersilie', 'Becher', 0.5),
('1020',   5, 'Petersilie', 'Becher', 0.5),
('1070',   5, 'Petersilie', 'Becher', 0.333)

ON CONFLICT (store_id, weekday, article_name) DO UPDATE SET base_qty = EXCLUDED.base_qty;

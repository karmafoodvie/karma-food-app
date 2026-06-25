-- ============================================================
-- FORECAST-MODUL: Portionsmengen pro Filiale/Tag/Gericht
-- Auto-Vorschlag aus Entsorgungsdaten + Store kann anpassen
-- ============================================================

-- 1) Der eigentliche Forecast-Wert pro Filiale/Datum/Gericht
CREATE TABLE IF NOT EXISTS forecast_qty (
  id SERIAL PRIMARY KEY,
  store_id TEXT NOT NULL REFERENCES stores(id),
  forecast_date DATE NOT NULL,
  dish_name TEXT NOT NULL,        -- 'Curry','Dal','Reis','Lasagne','Biryani','Gulasch','Salat'(Wochensalat)
  qty NUMERIC NOT NULL,           -- Portionen
  source TEXT NOT NULL DEFAULT 'auto', -- 'auto' = aus Entsorgungsdaten berechnet, 'manual' = von Store überschrieben
  changed_by TEXT,
  changed_at TIMESTAMPTZ,
  UNIQUE(store_id, forecast_date, dish_name)
);
ALTER TABLE forecast_qty ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public read forecast_qty" ON forecast_qty FOR SELECT USING (true);
CREATE POLICY "public write forecast_qty" ON forecast_qty FOR ALL USING (true);

-- 2) Wochensalat-Restbestand: Meldung am Schichtende, steuert Nachproduktion am nächsten Morgen
CREATE TABLE IF NOT EXISTS wochensalat_restbestand (
  id SERIAL PRIMARY KEY,
  store_id TEXT NOT NULL REFERENCES stores(id),
  report_date DATE NOT NULL,      -- Tag der Meldung (Schichtende)
  rest_qty NUMERIC,                -- was noch übrig ist
  needed_qty NUMERIC,              -- was für morgen gebraucht wird (Einschätzung der Filiale)
  note TEXT,
  changed_by TEXT,
  changed_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(store_id, report_date)
);
ALTER TABLE wochensalat_restbestand ENABLE ROW LEVEL SECURITY;
CREATE POLICY "public read wochensalat" ON wochensalat_restbestand FOR SELECT USING (true);
CREATE POLICY "public write wochensalat" ON wochensalat_restbestand FOR ALL USING (true);

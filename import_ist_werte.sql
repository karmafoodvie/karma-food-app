-- Echte IST-Bestände aus den Google Sheets importieren (Stand: Juni 2026)
-- Store-Mapping: 1070=Neustiftgasse, 1020=Ausstellungsstraße, boerse=Börse 1010, 3400=Stadtplatz
-- LB (Laurenzerberg) und Kitchen haben aktuell keine eigene Produktbestellung-Liste — werden nicht befüllt

DO $$
DECLARE
  today date := current_date;
BEGIN
  -- 1070 Neustiftgasse
  INSERT INTO kc_stock (store_id, article_id, ist_bestand, updated_date)
  SELECT '1070', id, v.ist, today FROM articles
  JOIN (VALUES
    ('Kashmiri Chili Crisp', 3.0), ('Korma Paste', 4.0), ('Madras Paste', 27.0),
    ('Masala Trio - Starter', 1.0), ('Masala Trio - Adventure', 1.0), ('Mama Masala', 3.0),
    ('Papa Masala', 3.0), ('Dal Masala', 11.0), ('Golden Salt', 7.0), ('Goa Masala', 6.0),
    ('BBQ Masala', 8.0), ('Chai Masala', 6.0), ('Mango Chilli Sauce', 4.0), ('Chai Sirup', 2.0),
    ('KARMA LUNCH CLUB BAG', 10.0), ('Kochbuch alt', 0.0), ('Kochbuch Curry', 0.0), ('Weducer Cup', 1.0)
  ) AS v(name, ist) ON articles.name = v.name
  ON CONFLICT (store_id, article_id) DO UPDATE SET ist_bestand = EXCLUDED.ist_bestand, updated_date = EXCLUDED.updated_date;

  -- 1020 Ausstellungsstraße
  INSERT INTO kc_stock (store_id, article_id, ist_bestand, updated_date)
  SELECT '1020', id, v.ist, today FROM articles
  JOIN (VALUES
    ('Kashmiri Chili Crisp', 0.0), ('Korma Paste', 9.0), ('Curry Paste', 7.0), ('Madras Paste', 5.0),
    ('Masala Trio - Starter', 4.0), ('Masala Trio - Adventure', 4.0), ('Mama Masala', 4.0),
    ('Papa Masala', 6.0), ('Dal Masala', 4.0), ('Golden Salt', 3.0), ('Goa Masala', 5.0),
    ('BBQ Masala', 7.0), ('Chai Masala', 3.0), ('Mango Chilli Sauce', 3.0), ('Chai Sirup', 5.0),
    ('KARMA LUNCH CLUB BAG', 10.0), ('Kochbuch alt', 0.0), ('Kochbuch Curry', 0.0), ('Weducer Cup', 4.0)
  ) AS v(name, ist) ON articles.name = v.name
  ON CONFLICT (store_id, article_id) DO UPDATE SET ist_bestand = EXCLUDED.ist_bestand, updated_date = EXCLUDED.updated_date;

  -- Börse 1010
  INSERT INTO kc_stock (store_id, article_id, ist_bestand, updated_date)
  SELECT 'boerse', id, v.ist, today FROM articles
  JOIN (VALUES
    ('Kashmiri Chili Crisp', 2.0), ('Korma Paste', 6.0), ('Curry Paste', 5.0), ('Madras Paste', 7.0),
    ('Masala Trio - Starter', 1.0), ('Masala Trio - Adventure', 2.0), ('Mama Masala', 5.0),
    ('Papa Masala', 4.0), ('Dal Masala', 5.0), ('Golden Salt', 5.0), ('Goa Masala', 5.0),
    ('BBQ Masala', 5.0), ('Chai Masala', 5.0), ('Mango Chilli Sauce', 3.0), ('Chai Sirup', 2.0),
    ('KARMA LUNCH CLUB BAG', 9.0), ('Kochbuch alt', 0.0), ('Kochbuch Curry', 0.0), ('Weducer Cup', 2.0)
  ) AS v(name, ist) ON articles.name = v.name
  ON CONFLICT (store_id, article_id) DO UPDATE SET ist_bestand = EXCLUDED.ist_bestand, updated_date = EXCLUDED.updated_date;

  -- Stadtplatz 3400 (ohne Redy2eat Tikka Masala Curry, gibt es nicht mehr)
  INSERT INTO kc_stock (store_id, article_id, ist_bestand, updated_date)
  SELECT '3400', id, v.ist, today FROM articles
  JOIN (VALUES
    ('Korma Paste', 8.0), ('Curry Paste', 4.0), ('Madras Paste', 6.0),
    ('Masala Trio - Starter', 1.0), ('Masala Trio - Adventure', 1.0), ('Mama Masala', 7.0),
    ('Papa Masala', 5.0), ('Dal Masala', 5.0), ('Golden Salt', 5.0), ('Goa Masala', 5.0),
    ('BBQ Masala', 5.0), ('Chai Masala', 5.0), ('Mango Chilli Sauce', 3.0), ('Chai Sirup', 4.0),
    ('KARMA LUNCH CLUB BAG', 8.0), ('Kochbuch alt', 1.0), ('Kochbuch Curry', 1.0), ('Weducer Cup', 5.0)
  ) AS v(name, ist) ON articles.name = v.name
  ON CONFLICT (store_id, article_id) DO UPDATE SET ist_bestand = EXCLUDED.ist_bestand, updated_date = EXCLUDED.updated_date;
END $$;

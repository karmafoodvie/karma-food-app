-- Fehlende KC / Webshop-Produkte aus Bestellliste Shop 1020 ergänzen
INSERT INTO articles (category, name, unit, min_stock, sort_order) VALUES
  ('Webshop-Produkte','Kashmiri Chili Crisp','Stk',3,80),
  ('Webshop-Produkte','Korma Paste','Stk',8,81),
  ('Webshop-Produkte','Curry Paste','Stk',8,82),
  ('Webshop-Produkte','Madras Paste','Stk',8,83),
  ('Webshop-Produkte','Masala Trio - Starter','Stk',2,84),
  ('Webshop-Produkte','Masala Trio - Adventure','Stk',2,85),
  ('Webshop-Produkte','Mama Masala','Stk',5,86),
  ('Webshop-Produkte','Papa Masala','Stk',5,87),
  ('Webshop-Produkte','Dal Masala','Stk',5,88),
  ('Webshop-Produkte','Golden Salt','Stk',5,89),
  ('Webshop-Produkte','Goa Masala','Stk',5,90),
  ('Webshop-Produkte','BBQ Masala','Stk',5,91),
  ('Webshop-Produkte','Chai Masala','Stk',5,92),
  ('Webshop-Produkte','Mango Chilli Sauce','Stk',3,93),
  ('Webshop-Produkte','Chai Sirup','Stk',3,94),
  ('Webshop-Produkte','KARMA LUNCH CLUB BAG','Stk',10,95),
  ('Webshop-Produkte','Kochbuch alt','Stk',3,96),
  ('Webshop-Produkte','Kochbuch Curry','Stk',3,97),
  ('Webshop-Produkte','Weducer Cup','Stk',2,98)
ON CONFLICT DO NOTHING;

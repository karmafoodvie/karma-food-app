-- Stores aktualisieren mit neuen Namen, Farben und PINs
DELETE FROM stores;

INSERT INTO stores (id, name, pin, image_url) VALUES
  ('lb',       'Laurenzerberg 1010',              '5500', NULL),
  ('boerse',   'Börse 1010',                      '2626', NULL),
  ('1020',     'Ausstellungsstraße 1020',          '1020', NULL),
  ('1070',     'Neustiftgasse 1070',               '1070', NULL),
  ('3400',     'Stadtplatz 3400',                  '3400', NULL),
  ('kitchen',  'Kitchen 3400',                     '3401', NULL),
  ('zentrale', 'Zentrale / Transporter',           '9999', NULL);

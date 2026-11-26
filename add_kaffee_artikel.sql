-- Kaffee (Espresso Intenso, ganze Bohne) für die Bestellliste der Stores und die Transporter-Liste (26.11.26)
INSERT INTO articles (category, name, unit, min_stock, sort_order, image_url, verfuegbar, archiviert)
SELECT 'Food & Drinks','Kaffee Espresso Intenso (Bohne, 500 g)','Pkg',2,35,'/images/products/kaffee-espresso-intenso.jpg',true,false
WHERE NOT EXISTS (SELECT 1 FROM articles WHERE name ILIKE 'Kaffee Espresso Intenso%');

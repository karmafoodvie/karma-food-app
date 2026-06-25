-- Sweets-Produktnamen anpassen (genauere Bezeichnung)
UPDATE articles SET name = 'Tahini Banana Muffin' WHERE name = 'Tahini Bananen Muffin';
UPDATE articles SET name = 'Raw Cake Chocolate Hazelnut' WHERE name = 'Raw Cake Chocolate';
UPDATE articles SET name = 'Raw Cake Raspberry Passionfruit' WHERE name = 'Raw Cake Passion Fruit';
UPDATE articles SET name = 'Choco Coco Cake' WHERE name = 'Choco Coconut Cake';

-- Bareballs (bereits vorhanden unter Food & Drinks) auf genauere Namen umbenennen - NICHT neu anlegen
UPDATE articles SET name = 'Bareball White Chocolate Almond' WHERE name = 'Bareballs White Almond';
UPDATE articles SET name = 'Bareball Peanut Caramel' WHERE name = 'Bareballs Peanut';

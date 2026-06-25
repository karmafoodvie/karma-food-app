-- Duplikate entfernen (IDs 104 und 105 sind die versehentlich doppelt angelegten)
DELETE FROM articles WHERE id IN (104, 105);

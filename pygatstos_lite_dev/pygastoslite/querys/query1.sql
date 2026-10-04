-- SQLite
-- Cambiar sync de id=1
UPDATE entry
SET sync = 0
WHERE id = 1;

-- Cambiar sync de id=2
UPDATE entry
SET sync = 0
WHERE id = 2;

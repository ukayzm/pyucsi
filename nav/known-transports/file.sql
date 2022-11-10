PRAGMA foreign_keys = ON;

/*
 * file
 */
DELETE FROM transports WHERE src_key IN (SELECT src_key FROM sources WHERE delivery_system = 8);


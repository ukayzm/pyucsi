PRAGMA foreign_keys = ON;

/*
 * JCSAT 3A
 */
DELETE FROM transports WHERE src_key IN (SELECT src_key FROM sources WHERE src_name = "JCSAT 3A");

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "JCSAT 3A";
INSERT INTO ts_params_sat (ts_key, freq, polarization, symbol_rate, fec_inner, modulation_system) VALUES (last_insert_rowid(), 12658, 1, 21096, 0, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "JCSAT 3A";
INSERT INTO ts_params_sat (ts_key, freq, polarization, symbol_rate, fec_inner, modulation_system) VALUES (last_insert_rowid(), 12643, 0, 21096, 0, 0);


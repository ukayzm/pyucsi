PRAGMA foreign_keys = ON;

/*
 * Freesat Home transponder
 * - Eutelsat 28A in Astra 28.2E fleet
 * - 11.428 GHz, H, 27.5 Mbaud, 2/3
 */
DELETE FROM transports WHERE src_key IN (SELECT src_key FROM sources WHERE src_name = "Astra 28.2E");

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Astra 28.2E";
INSERT INTO ts_params_sat (ts_key, freq, polarization, modulation_system, symbol_rate, fec_inner) VALUES (last_insert_rowid(), 11428, 0, 0, 27500, 2);
INSERT INTO ts_home (ts_key, operator) VALUES (last_insert_rowid(), "Freesat");

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Astra 28.2E";
INSERT INTO ts_params_sat (ts_key, freq, polarization, modulation_system, symbol_rate, fec_inner) VALUES (last_insert_rowid(), 10847, 1, 0, 22000, 4);


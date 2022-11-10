PRAGMA foreign_keys = ON;

/*
 * CanalSat (TNTSAT) Reference TP
 * - Astra 19.2E
 * - 11.856 GHz, V, 27500 kS/s
 * - 12.402 GHz, V, 27500 kS/s
 */
DELETE FROM transports WHERE src_key IN (SELECT src_key FROM sources WHERE src_name = "Astra 19.2E");

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Astra 19.2E";
INSERT INTO ts_params_sat (ts_key, freq, polarization, symbol_rate) VALUES (last_insert_rowid(), 11856, 1, 27500);
INSERT INTO ts_home (ts_key, operator) VALUES (last_insert_rowid(), "CanalSat");

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Astra 19.2E";
INSERT INTO ts_params_sat (ts_key, freq, polarization, symbol_rate) VALUES (last_insert_rowid(), 12402, 1, 27500);
INSERT INTO ts_home (ts_key, operator) VALUES (last_insert_rowid(), "CanalSat");


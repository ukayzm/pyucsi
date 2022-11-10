PRAGMA foreign_keys = ON;

/*
 * APS Anchor TP
 * - Astra 19.2E
 * - 12.603 GHz, H, 22000 kS/s, 5/6
 * - 12.552 GHz, V, 22000 kS/s, 5/6
 * - 10.832 GHz, H, 22000 kS/s, 5/6
 */
DELETE FROM transports WHERE src_key IN (SELECT src_key FROM sources WHERE src_name = "Astra 19.2E");
INSERT OR IGNORE INTO operators (op_name) VALUES "APS";

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Astra 19.2E";
-- UPDATE transports SET op_key = (SELECT op_key from operators where src_name = "APS") where src_key = last_insert_rowid();
INSERT INTO ts_params_sat (ts_key, freq, polarization, symbol_rate, fec_inner) VALUES (last_insert_rowid(), 12603, 0, 22000, 4);
INSERT INTO ts_home (ts_key, operator) VALUES (last_insert_rowid(), "APS");

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Astra 19.2E";
INSERT INTO ts_params_sat (ts_key, freq, polarization, symbol_rate, fec_inner) VALUES (last_insert_rowid(), 12552, 1, 22000, 4);
INSERT INTO ts_home (ts_key, operator) VALUES (last_insert_rowid(), "APS");

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Astra 19.2E";
INSERT INTO ts_params_sat (ts_key, freq, polarization, symbol_rate, fec_inner) VALUES (last_insert_rowid(), 10832, 0, 22000, 4);
INSERT INTO ts_home (ts_key, operator) VALUES (last_insert_rowid(), "APS");


PRAGMA foreign_keys = ON;

/*
 * VAST Home TP
 * - Optus 156.0E
 * - 12.567 GHz, V, 30000 kS/s, 3/5, DVB-S2
 */
DELETE FROM transports WHERE src_key IN (SELECT src_key FROM sources WHERE src_name = "Optus 156.0E");

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Optus 156.0E";
INSERT INTO ts_params_sat (ts_key, freq, polarization, symbol_rate, fec_inner, modulation_system) VALUES (last_insert_rowid(), 12567, 1, 30000, 7, 1);
INSERT INTO ts_home (ts_key, operator, net_search) VALUES (last_insert_rowid(), "VAST", 1);


/*
 * Aurora
 * - Optus 156.0E
 * - 12.407 GHz, V, 30000 kS/s, 2/3, DVB-S
 */
INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Optus 156.0E";
INSERT INTO ts_params_sat (ts_key, freq, polarization, symbol_rate, fec_inner, modulation_system) VALUES (last_insert_rowid(), 12407, 1, 30000, 2, 0);


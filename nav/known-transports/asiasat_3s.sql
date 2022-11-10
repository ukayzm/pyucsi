PRAGMA foreign_keys = ON;

/*
 * AsiaSAT 3S
 */
DELETE FROM transports WHERE src_key IN (SELECT src_key FROM sources WHERE src_name = "AsiaSAT 3S");

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "AsiaSAT 3S";
INSERT INTO ts_params_sat (ts_key, freq, polarization, symbol_rate, fec_inner, modulation_system) VALUES (last_insert_rowid(), 3780, 1, 28100, 0, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "AsiaSAT 3S";
INSERT INTO ts_params_sat (ts_key, freq, polarization, symbol_rate, fec_inner, modulation_system) VALUES (last_insert_rowid(), 3860, 1, 27500, 0, 0);

-- 3840 MHz, H, 26850, 7/8, DVB-S
INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "AsiaSAT 3S";
INSERT INTO ts_params_sat (ts_key, freq, polarization, symbol_rate, fec_inner, modulation_system) VALUES (last_insert_rowid(), 3840, 0, 26850, 0, 0);

PRAGMA foreign_keys = ON;

/*
 * Primacom Home transponder -- S27 to S31
 * 354000, 362000, 370000, 378000, 386000
 */
DELETE FROM transports WHERE src_key IN (SELECT src_key FROM sources WHERE src_name = "Primacom");

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Primacom";
INSERT INTO ts_params_cab (ts_key, freq, symbol_rate) VALUES (last_insert_rowid(), 354000, 6900);
INSERT INTO ts_home (ts_key, operator) VALUES (last_insert_rowid(), "Primacom");

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Primacom";
INSERT INTO ts_params_cab (ts_key, freq, symbol_rate) VALUES (last_insert_rowid(), 362000, 6900);
INSERT INTO ts_home (ts_key, operator) VALUES (last_insert_rowid(), "Primacom");

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Primacom";
INSERT INTO ts_params_cab (ts_key, freq, symbol_rate) VALUES (last_insert_rowid(), 37000, 6900);
INSERT INTO ts_home (ts_key, operator) VALUES (last_insert_rowid(), "Primacom");

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Primacom";
INSERT INTO ts_params_cab (ts_key, freq, symbol_rate) VALUES (last_insert_rowid(), 378000, 6900);
INSERT INTO ts_home (ts_key, operator) VALUES (last_insert_rowid(), "Primacom");

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Primacom";
INSERT INTO ts_params_cab (ts_key, freq, symbol_rate) VALUES (last_insert_rowid(), 386000, 6900);
INSERT INTO ts_home (ts_key, operator) VALUES (last_insert_rowid(), "Primacom");


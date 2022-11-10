PRAGMA foreign_keys = ON;

/*
 * Sweden terrestrial
 */
DELETE FROM transports WHERE src_key IN (SELECT src_key FROM sources WHERE src_name = "Sweden");

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Sweden";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 490000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Sweden";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 642000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Sweden";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 706000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Sweden";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 730000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Sweden";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 746000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Sweden";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 754000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Sweden";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 778000, 0);


PRAGMA foreign_keys = ON;

/*
 * terrestrial for LAB TEST
 */
DELETE FROM transports WHERE src_key IN (SELECT src_key FROM sources WHERE src_name = "TEST-TER");

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "TEST-TER";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 482000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "TEST-TER";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 490000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "TEST-TER";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 514000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "TEST-TER";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 538000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "TEST-TER";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 546000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "TEST-TER";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 570000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "TEST-TER";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 586000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "TEST-TER";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 602000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "TEST-TER";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 618000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "TEST-TER";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 626000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "TEST-TER";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 706000, 0);


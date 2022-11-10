PRAGMA foreign_keys = ON;

/*
 * UK terrestrial
 */
DELETE FROM transports WHERE src_key IN (SELECT src_key FROM sources WHERE src_name = "UK");

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 474000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 482000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 490000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 498000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 506000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 514000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 522000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 530000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 538000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 546000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 554000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 562000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 570000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 578000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 586000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 594000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 602000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 610000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 618000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 626000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 634000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 642000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 650000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 658000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 666000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 674000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 682000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 690000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 698000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 706000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 714000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 722000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 730000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 738000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 746000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 754000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 762000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 770000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 778000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 786000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 794000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 802000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 810000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 818000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 826000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 834000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 842000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 850000, 0);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "UK";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 858000, 0);


PRAGMA foreign_keys = ON;

/*
 * Australia terrestrial
 */
DELETE FROM transports WHERE src_key IN (SELECT src_key FROM sources WHERE src_name = "Australia");

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 177500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 184500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 191500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 198500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 205500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 212500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 219500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 226500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 522500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 529500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 536500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 543500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 550500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 557500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 564500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 571500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 578500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 585500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 592500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 599500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 606500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 613500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 620500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 627500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 634500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 641500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 648500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 655500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 662500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 669500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 676500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 683500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 690500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 697500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 704500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 711500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 718500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 725500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 732500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 739500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 746500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 753500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 760500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 767500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 774500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 781500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 788500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 795500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 802500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 809500, 1);

INSERT INTO transports (src_key) SELECT src_key FROM sources WHERE src_name = "Australia";
INSERT INTO ts_params_ter (ts_key, freq, bandwidth) VALUES (last_insert_rowid(), 816500, 1);


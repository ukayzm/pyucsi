/***************************************************************************
                          installation  examples
 ***************************************************************************/

INSERT INTO tuners (capability, type, name) VALUES (0, 0, "SAT tuner 1");
INSERT INTO tuners (capability, type, name) VALUES (0, 0, "SAT tuner 2");

/* plain LNB */
INSERT INTO lnbs (lo_freq, lo_freq2, num_output, with_motor, name) VALUES (5150, 0, 1, 0, "most common LNB");
INSERT INTO lnbs (lo_freq, lo_freq2, num_output, with_motor, name) VALUES (9750, 10600, 1, 0, "universal LNB");

INSERT INTO sat_lnbs (src_key, lnb_key, position, tone_burst)
       SELECT src_key, lnb_key, 0, 0 FROM sources JOIN lnbs
       WHERE sources.name = "Astra 19.2E" AND lnbs.name = "most common LNB";


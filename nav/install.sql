PRAGMA foreign_keys = ON;


/***************************************************************************
                  This file contains the installation.
 ***************************************************************************/


/***************************************************************************
           schema to contain tuners (common to all types of network)
 ***************************************************************************/

CREATE TABLE tuners (
	tuner_key INTEGER PRIMARY KEY,
	type INTEGER,              -- fe_type defined by linuxtv.
	capability INTEGER,        -- flags of capability defined by linuxtv.
	is_slave INTEGER,          -- boolean
	                           -- 0 if this tuner is for non-QPSK.
	                           --   or if this tuner can control LNB (master).
	                           -- 1 if this tuner cannot control LNB (slave).
	                           -- A tuner is slave if it is physically linked
	                           -- by loop-thourth cable from other tuner
	                           -- or non-power-through port of signal spllitter.
	                           -- A slave tuner shares LNB with a master tuner
	                           -- but not necessarily.
	tuner_name TEXT,           -- given by user
	                           -- CAUTION: tuner_name is case-sensitive
	                           --          and used as search-key.
	UNIQUE (tuner_name)
);


/***************************************************************************
    CAB, TER: schema to contain the associations of sources and tuners
 ***************************************************************************/

/*
 * associates sources with tuners
 */
CREATE TABLE src_tuners (
	src_key INTEGER,
	tuner_key INTEGER,
	-- FOREIGN KEY (src_key) REFERENCES sources ON DELETE CASCADE,
	FOREIGN KEY (tuner_key) REFERENCES tuners ON DELETE CASCADE
);


/***************************************************************************
  SAT: schema to contain the signal path from satellite to tuner

  For satellite, LNB is located between source and tuner, which makes
  the things complex.

  You can get src to tuner table (like a table src_tuners) with this query:

      select sat_lnbs.src_key as src_key, lnb_tuners.tuner_key as tuner_key
        from sat_lnbs
        join lnbs on sat_lnbs.lnb_key = lnbs.lnb_key
        join lnb_tuners on lnbs.lnb_key = lnb_tuners.lnb_key;

 ***************************************************************************/

/*
 * This table contains LNB (or dish) properties.
 *
 * LNB is located on dish and plays a role of receiving signal from satellite.
 * There are many types of LNB:
 *  - Basic LNB: has one oscillator, one output.
 *  - Universal LNB: has two oscillators (9.75GHz and 10.6GHz), one output.
 *  - Twin/quad/octo LNB: has 2/4/8 outputs which can operate independently
 *    from each other.
 *  - SCD can also have multiple outputs.
 *  - Quattro LNB with multiswitch: is considered as universal LNB.
 */
CREATE TABLE lnbs (
	lnb_key INTEGER PRIMARY KEY AUTOINCREMENT,
	lo_freq INTEGER,    -- local oscillator frequency in MHz.
	                    -- Typical value is: 5150, 5750, 9750, 10000,
	                    -- 10600, 10700, 10750, 11200, 11300, 11475, 11500, ...
	lo_freq2 INTEGER,   -- frequency in MHz of the second local oscillator.
	                    -- for the case of universal-LNB
	                    -- selected by 22kHz tone
	num_output INTEGER, -- number of outputs independent from each other
	                    -- ex) twin/quad/octo LNBs is 2/4/8.
	with_motor INTEGER, -- boolean
	                    -- 1 if this LNB is installed in a dish with motor.
	lnb_name TEXT       -- given by user
);

/*
 * associates satellites (sources) with LNBs.
 * Typically one LNB is associated with one satellite.
 * A dual-LNB (monoblock LNB) is associated with two satellites
 * selected by tone_burst.
 * An LNB in a dish with motor is associated with multiple satellites
 * and its positions.
 */
CREATE TABLE sat_lnbs (
	src_key INTEGER,
	lnb_key INTEGER,
	position INTEGER,     -- for a dish with motor
	tone_burst INTEGER,   -- 0: tone_burst is not used
	                      -- 1: tone burst A (a dual-LNB to select satellite A)
	                      -- 2: tone burst B (a dual-LNB to select satellite B)
	-- FOREIGN KEY (src_key) REFERENCES sources ON DELETE CASCADE,
	FOREIGN KEY (lnb_key) REFERENCES lnbs ON DELETE CASCADE
);

/*
 * associates tuners with LNBs -- which tuner is connected to which LNB and how.
 * This table represents the path between LNB and tuner.
 * A tuner without DiSEqC switch is associated with one LNB (link_type 0).
 * A tuner connected with DiSEqC 1.0 switch is associated with maximum 4 LNBs.
 */
CREATE TABLE lnb_tuners (
	lnb_key INTEGER NOT NULL,
	tuner_key INTEGER NOT NULL,
	link_type INTEGER,         -- 0 if DiSEqC is not used
	                           -- 1 for DiSEqC A
	                           -- 2 for DiSEqC B
	                           -- 3 for DiSEqC C
	                           -- 4 for DiSEqC D
	diseqc_version INTEGER,    -- 0 if DiSEqC is not used
	                           -- 11 for DiSEqC 1.1, etc.
	continuous_tone INTEGER,   -- boolean
	                           -- 0: this link does not need 22kHz tone
	                           --    or 22kHz tone is used to select lo_freq.
	                           -- 1: this link needs continuous 22kHz tone
	                           --    to select LNB (satellite)
	scd_band INTEGER,          -- 0 for LNB without SCD
	                           --   or user band (1 ~ 8) for SCD
	scd_freq INTEGER,          -- 0 for LNB without SCD
	                           --   or user band frequency in kHz for SCD
	FOREIGN KEY (tuner_key) REFERENCES tuners ON DELETE CASCADE,
	FOREIGN KEY (lnb_key) REFERENCES lnbs ON DELETE CASCADE
);


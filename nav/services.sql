PRAGMA foreign_keys = ON;


/***************************************************************************
                       schema to contain source information
 ***************************************************************************/

/*
 * Source of Transport Stream
 *   SAT: a group of broadcast satellites located close in space
 *   CAB: local cable distribution
 *   TER: country or location of the receiving antenna
 *
 * Do not delete entries if you don't know what you are doing.
 */
CREATE TABLE sources (
	src_key INTEGER PRIMARY KEY AUTOINCREMENT,
	delivery_system INTEGER,   -- 0 for satellite
	                           -- 1 for cable
	                           -- 2 for terrestrial
	                           -- 8 for file
	                           -- 9 for unknown
	src_name CHAR,             -- given by user
	                           -- CAUTION: src_name is case-sensitive
	                           --          and used as search-key.
	orbital_position INTEGER,  -- only for satellite
	                           -- ex) -125 means 12.5 degree, western.
	                           --     192 means 19.2 degree, eastern.
	description CHAR,          -- given by user for help
	UNIQUE (src_name)
);

/* TODO: replace ts_home with this table */
CREATE TABLE operators (
	op_key INTEGER PRIMARY KEY AUTOINCREMENT,
	op_name CHAR,              -- given by user
	                           -- CAUTION: op_name is case-sensitive
	                           --          and used as search-key.
	UNIQUE (op_name)
);


/***************************************************************************
                    schema to contain service information
 ***************************************************************************/

CREATE TABLE networks (
	nid INTEGER PRIMARY KEY,   -- network_id in NIT
	net_name CHAR              -- network_name in network_name_descriptor
);

CREATE TABLE network_names (
	nid INTEGER,    -- nid is not a primary key because
	                -- there may be multiple records for an nid.
	lang CHAR,      -- ISO 639 language code
	net_name CHAR,  -- network_name in multilingual_network_name_descriptor
	FOREIGN KEY (nid) REFERENCES networks ON DELETE CASCADE
);

/*
 * table to contain transport stream (TS)
 * Usually TS can be uniquely identified by tsid and onid.
 * But sometimes duplicated tsid and onid pair may be found,
 * especially at the border of terrestrial cell where user may receive signals
 * from multiple transmitters.
 */
CREATE TABLE transports (
	ts_key INTEGER PRIMARY KEY AUTOINCREMENT,
	nid INTEGER,
	tsid INTEGER,
	onid INTEGER,
	src_key INTEGER NOT NULL,
	op_key INTEGER,
	is_home_tp INTEGER,        -- boolean
	net_search_needed INTEGER, -- boolean
	ts_name CHAR,              -- given by user for help
	time_offset INTEGER,       -- representative time offset in minute
	                           -- TODO: delete it
	FOREIGN KEY (nid) REFERENCES networks ON DELETE CASCADE,
	--FOREIGN KEY (op_key) REFERENCES operators ON DELETE CASCADE,
	FOREIGN KEY (src_key) REFERENCES sources ON DELETE CASCADE
);

CREATE TABLE time_offset (
	ts_key INTEGER,
	country_code CHAR,
	region_id INTEGER,
	local_time_offset INTEGER, -- in minute
	time_of_change INTEGER,    -- unixtime, UTC
	next_time_offset INTEGER,  -- in minute
	FOREIGN KEY (ts_key) REFERENCES transports ON DELETE CASCADE
);

/* parameters in terrestrial_delivery_system_descriptor */
CREATE TABLE ts_params_ter (
	ts_key INTEGER PRIMARY KEY,
	freq INTEGER,              -- decimal integer (in kHz)
	bandwidth INTEGER,         -- EN 300 468
	                           -- 0 for 8 MHz
	                           -- 1 for 7 MHz
	                           -- 2 for 6 MHz
	                           -- 3 for 5 MHz
	code_rate_HP INTEGER,      -- EN 300 468
	code_rate_LP INTEGER,      -- EN 300 468
	                           -- 0 for 1/2, 1 for 2/3, 2 for 3/4
	                           -- 3 for 5/6, 4 for 7/8
	constellation INTEGER,     -- EN 300 468
	                           -- 0 for QPSK
	                           -- 1 for 16-QAM
	                           -- 2 for 64-QAM
	transmission_mode INTEGER, -- EN 300 468
	                           -- 0 for 2k
	                           -- 1 for 8k
	                           -- 2 for 4k
	guard_interval INTEGER,    -- EN 300 468
	                           -- 0 for 1/32
	                           -- 1 for 1/16
	                           -- 2 for 1/8
	                           -- 3 for 1/4
	hierarchy_information INTEGER, -- EN 300 468
	                           -- 0 for non-hierarchical, native interleaver
	                           -- 1 for alpha = 1, native interleaver
	                           -- 2 for alpha = 2, native interleaver
	                           -- 3 for alpha = 4, native interleaver
	                           -- 4 for non-hierarchical, in-depth interleaver
	                           -- 5 for alpha = 1, in-depth interleaver
	                           -- 6 for alpha = 2, in-depth interleaver
	                           -- 7 for alpha = 4, in-depth interleaver
	signal_strength INTEGER,
	signal_quality INTEGER,
	FOREIGN KEY (ts_key) REFERENCES transports ON DELETE CASCADE
);

/* parameters in T2_delivery_system_descriptor (TODO) */
CREATE TABLE ts_params_ter2 (
	ts_key INTEGER PRIMARY KEY,
	plp_id INTEGER,
	t2_system_id INTEGER,
	FOREIGN KEY (ts_key) REFERENCES transports ON DELETE CASCADE
);

/* parameters in satellite_delivery_system_descriptor */
CREATE TABLE ts_params_sat (
	ts_key INTEGER PRIMARY KEY,
	freq INTEGER,              -- decimal integer (in MHz)
	orbital_position INTEGER,  -- decimal integer
	                           -- -125 means 12.5 degree, western.
	                           -- 192 means 19.2 degree, eastern.
	polarization INTEGER,      -- EN 300 468
	                           -- 0 for linear - horizontal
	                           -- 1 for linear - vertical
	                           -- 2 for circular - left
	                           -- 3 for circular - right
	roll_off INTEGER,          -- EN 300 468
	                           -- 0 for alpha = 0.35, DVB-S2
	                           -- 1 for alpha = 0.25, DVB-S2
	                           -- 2 for alpha = 0.20, DVB-S2
	                           -- no meaning for DVB-S
	modulation_system INTEGER, -- EN 300 468
	                           -- 0 for DVB-S
	                           -- 1 for DVB-S2
	modulation_type INTEGER,   -- EN 300 468
	                           -- 0 for Auto
	                           -- 1 for QPSK
	                           -- 2 for 8PSK
	                           -- 3 for 16-QAM (n/a for DVB-S2)
	symbol_rate INTEGER,       -- decimal integer (in kilo-symbol/s)
	fec_inner INTEGER,         -- EN 300 468
	                           -- 0 for not-defined
	                           -- 1 for 1/2, 2 for 2/3, 3 for 3/4
	                           -- 4 for 5/6, 5 for 7/8, 6 for 8/9
	                           -- 7 for 3/5, 8 for 4/5, 9 for 9/10
	signal_strength INTEGER,
	signal_quality INTEGER,
	FOREIGN KEY (ts_key) REFERENCES transports ON DELETE CASCADE
);

/* parameters in S2_satellite_delivery_system_descriptor */
CREATE TABLE ts_params_sat2 (
	ts_key INTEGER PRIMARY KEY,
	scrambling_sequence_index INTEGER,
	input_stream_identifier INTEGER,
	backwards_compatibility_indicator INTEGER,
	FOREIGN KEY (ts_key) REFERENCES transports ON DELETE CASCADE
);

/* parameters in cable_delivery_system_descriptor */
CREATE TABLE ts_params_cab (
	ts_key INTEGER PRIMARY KEY,
	freq INTEGER,              -- decimal integer (in kHz)
	fec_outer INTEGER,
	modulation INTEGER,
	symbol_rate INTEGER,       -- decimal integer (in kilo-symbol/s)
	fec_inner INTEGER,         -- EN 300 468
	                           -- 0 for not-defined
	                           -- 1 for 1/2, 2 for 2/3, 3 for 3/4
	                           -- 4 for 5/6, 5 for 7/8, 6 for 8/9
	                           -- 7 for 3/5, 8 for 4/5, 9 for 9/10
	FOREIGN KEY (ts_key) REFERENCES transports ON DELETE CASCADE
);

/* parameters to feed file */
CREATE TABLE ts_params_file (
	ts_key INTEGER PRIMARY KEY,
	pathname CHAR,
	FOREIGN KEY (ts_key) REFERENCES transports ON DELETE CASCADE
);

/* Home Transponders (a.k.a. reference TP or anchor TP) */
CREATE TABLE ts_home (
	ts_key INTEGER PRIMARY KEY,
	operator CHAR,      -- given by user
	                    -- CAUTION: operator is case-sensitive
	                    --          and used as search-key.
	net_search INTEGER, -- boolean
	                    -- 1 to enable network search
	FOREIGN KEY (ts_key) REFERENCES transports ON DELETE CASCADE
);

CREATE TABLE services (
	svc_key INTEGER PRIMARY KEY AUTOINCREMENT,
	ts_key INTEGER,
	svid INTEGER,
	type INTEGER,   -- service_type in service_descriptor
	svc_name CHAR,  -- service_name in service_descriptor
	prov_name CHAR, -- service_provider_name in service_descriptor
	ca INTEGER,
	UNIQUE (ts_key, svid),
	FOREIGN KEY (ts_key) REFERENCES transports ON DELETE CASCADE
);

CREATE TABLE service_names (
	svc_key INTEGER,    -- svc_key is not a primary key because
	                    -- there may be multiple records for a svc_key.
	lang CHAR,          -- ISO 639 language code
	svc_name CHAR,      -- service_name in multilingual_service_name_descriptor
	prov_name CHAR,     -- service_provider_name in multilingual_service_name_descriptor
	FOREIGN KEY (svc_key) REFERENCES services ON DELETE CASCADE
);
CREATE INDEX service_names_index ON service_names (svc_key);

/* for containing services while scanning */
CREATE TABLE services_temp (
	ts_key INTEGER,
	svid INTEGER,
	svc_name CHAR,
	prov_name CHAR,
	type INTEGER,
	ca INTEGER,
	PRIMARY KEY (ts_key, svid),
	FOREIGN KEY (ts_key) REFERENCES transports ON DELETE CASCADE
);

CREATE TABLE bouquets (
	bid INTEGER PRIMARY KEY,    -- bouquet_id
	bq_name CHAR                -- bouquet_name in bouquet_name_descriptor
);

CREATE TABLE bouquet_names (
	bid INTEGER,    -- bid is not a primary key because
	                -- there may be multiple records for a bid.
	lang CHAR,      -- ISO 639 language code
	bq_name CHAR,   -- bouquet_name in multilingual_bouquet_name_descriptor
	FOREIGN KEY (bid) REFERENCES bouquets ON DELETE CASCADE
);

/* associates services with bouquets */
CREATE TABLE bouquet_services (
	bid INTEGER,
	svc_key INTEGER,
	FOREIGN KEY (bid) REFERENCES bouquets ON DELETE CASCADE,
	FOREIGN KEY (svc_key) REFERENCES services ON DELETE CASCADE
);
CREATE INDEX bouquet_services_index ON bouquet_services (bid);

CREATE TABLE default_authorities_ts (
	ts_key INTEGER PRIMARY KEY,
	default_authority CHAR,
	FOREIGN KEY (ts_key) REFERENCES transports ON DELETE CASCADE
);

CREATE TABLE default_authorities (
	svc_key INTEGER PRIMARY KEY,
	default_authority CHAR,
	FOREIGN KEY (svc_key) REFERENCES services ON DELETE CASCADE
);

CREATE TABLE lcn (
	svc_key INTEGER,         -- svc_key is not a primary key because
	                         -- there may be multiple records for a svc_key.
	                         -- I.e., one service may have multiple LCN.
	visible INTEGER,
	selectable INTEGER,
	lcn INTEGER,
	FOREIGN KEY (svc_key) REFERENCES services ON DELETE CASCADE
);
CREATE INDEX lcn_svc_index ON lcn (svc_key);
CREATE INDEX lcn_index ON lcn (lcn);

/*
 * Saving stream informations in DB is not a good idea.
 * The following tables are for research and analysing.
 */
CREATE TABLE streams (
	strm_key INTEGER PRIMARY KEY AUTOINCREMENT,
	svc_key INTEGER,
	pid INTEGER,
	stream_type INTEGER,
	component_tag INTEGER,
	stream_class INTEGER,    -- 0: unclassified
	                         -- 1: video
	                         -- 2: audio
	                         -- 3: dvb_subtitle
	                         -- 4: teletext
	UNIQUE (svc_key, pid),
	FOREIGN KEY (svc_key) REFERENCES services ON DELETE CASCADE
);
CREATE INDEX streams_index ON streams (svc_key);

CREATE TABLE streams_audio (
	strm_key INTEGER,        -- strm_key is not a primary key because
	                         -- there may be multiple records for a strm_key.
	lang CHAR,               -- ISO 639 language code
	codec INTEGER,           -- 1: MPEG (mono left), 2: MPEG (mono right)
	                         -- 3: MPEG (stereo)
	                         -- 4: AC3, 5: E-AC3, 6: DTS, 7: AAC
	                         -- 8: HE-AAC v1, 9: HE-AAC v2
	audio_type INTEGER,      -- based on ISO 13818-1
	mix_type INTEGER,
	editorial_classification INTEGER,
	num_channel INTEGER,
	FOREIGN KEY (strm_key) REFERENCES streams ON DELETE CASCADE
);
CREATE INDEX streams_audio_index ON streams_audio (strm_key);

CREATE TABLE streams_dvb_subtitle (
	strm_key INTEGER,        -- strm_key is not a primary key because
	                         -- there may be multiple records for a strm_key.
	lang CHAR,               -- ISO 639 language code
	subtitling_type INTEGER, -- based on EN 300 468
	composition_page_id INTEGER,
	ancillary_page_id INTEGER,
	FOREIGN KEY (strm_key) REFERENCES streams ON DELETE CASCADE
);
CREATE INDEX streams_dvb_subtitle_index ON streams_dvb_subtitle (strm_key);

CREATE TABLE streams_teletext (
	strm_key INTEGER,        -- strm_key is not a primary key because
	                         -- there may be multiple records for a strm_key.
	lang CHAR,               -- ISO 639 language code
	teletext_type INTEGER,
	magazine_number INTEGER,
	page_number INTEGER,
	FOREIGN KEY (strm_key) REFERENCES streams ON DELETE CASCADE
);
CREATE INDEX streams_teletext_index ON streams_teletext (strm_key);


/***************************************************************************
                  schema to contain reservation and schedule
 ***************************************************************************/

/* lookup table for actions */
CREATE TABLE rsv_actions (
	action INTEGER PRIMARY KEY,
	action_name CHAR NOT NULL
);
INSERT INTO rsv_actions VALUES (1,  "turn on into standby mode");
INSERT INTO rsv_actions VALUES (2,  "turn on into operation mode");
INSERT INTO rsv_actions VALUES (3,  "enter into standby mode");
INSERT INTO rsv_actions VALUES (10, "watch");
INSERT INTO rsv_actions VALUES (11, "record");
INSERT INTO rsv_actions VALUES (12, "update channel list");
INSERT INTO rsv_actions VALUES (13, "collect EIT");
INSERT INTO rsv_actions VALUES (14, "update S/W (OTA)");
INSERT INTO rsv_actions VALUES (15, "notify to user");
INSERT INTO rsv_actions VALUES (16, "refresh current time");
INSERT INTO rsv_actions VALUES (17, "update EMM");
INSERT INTO rsv_actions VALUES (18, "execute installation wizard");

/* reservations */
CREATE TABLE reservations (
	rsv_key INTEGER PRIMARY KEY AUTOINCREMENT,
	deactivated INTEGER DEFAULT 0,
	rsv_name CHAR NOT NULL,
	description CHAR DEFAULT "",

	action INTEGER NOT NULL,    -- refer to table rsv_actions
	target INTEGER DEFAULT 0,   -- 0 N/A
	                            -- 1 a service
	                            -- 2 an event
	                            -- 3 a keyword
	                            -- 4 a program CRID
	                            -- 5 a series CRID
	svc_key INTEGER DEFAULT 0,  -- non-zero for a target involved in a service.
	                            -- In case of CRID-based reservation, this
	                            -- field specifies a preferred service.
	evid INTEGER DEFAULT 0,     -- non-zero for a target involved in an event.
	                            -- In case of CRID-based reservation, this
	                            -- field specifies a preferred event.

	do_when INTEGER DEFAULT 0,  -- 0 N/A. That is, whenever available
	                            -- 1 at a daily time
	                            -- 2 at a specific system tick
	                            -- 3 when entering into standby mode
	                            -- 4 when entering into operation mode
	replan_when INTEGER DEFAULT 0, -- specifies when to replan the
	                            -- reservation or its schedules
	                            -- These bitfield values can be OR-ed:
	                            -- non-zero value will trigger replanning
	                            -- 1   (0x01) when finishing schedule
	                            -- 2   (0x02) when exiting from operation
	                            -- 4   (0x04) when entering into operation
	                            -- 8   (0x04) when entering into standby
	                            -- 16  (0x10) on EIT completion
	                            -- 32  (0x20) when changing channel
	                            -- 64  (0x40) when changing mux in tuner
	                            -- 128 (0x80) on change of time/offset

	booked_time INTEGER DEFAULT (strftime('%s', 'now')),
	priority INTEGER DEFAULT 0, -- the lower value, the higher priority
	directory CHAR DEFAULT "",  -- destination directory to save file
	                            -- for recording or downloading
	FOREIGN KEY (action) REFERENCES rsv_actions,
	FOREIGN KEY (svc_key) REFERENCES services ON DELETE CASCADE
);

/* reservations at a daily time (repeatedly) */
CREATE TABLE rsvs_daily (
	rsv_key INTEGER PRIMARY KEY,
	yyyymmdd INTEGER DEFAULT 0, -- 8-digits decimal integer; YYYYMMDD
	                            --   date of starting point
	                            --   0 means starting today
	hhmmss INTEGER NOT NULL,    -- 5 or 6-digits decimal integer; HHMMSS
	duration INTEGER DEFAULT 0, -- in seconds
	                            -- 0 if it has no duration or the duration
	                            -- cannot be determined.
	day_of_week INTEGER DEFAULT 0, -- flag for day of week.
	                            -- 0 for non-repeating.
	                            -- 1  (0x01) on every Sunday
	                            -- 2  (0x02) on every Monday
	                            -- 4  (0x04) on every Tuesday
	                            -- 8  (0x08) on every Wednesday
	                            -- 16 (0x10) on every Thursday
	                            -- 32 (0x20) on every Friday
	                            -- 64 (0x40) on every Saturday
	                            -- These bitfield values can be OR-ed:
	                            -- 0x41 on every weekend,
	                            -- 0x3e on every weekday, 0x7f on everyday
	FOREIGN KEY (rsv_key) REFERENCES reservations ON DELETE CASCADE
);

/*
 * reservations at a specific system tick (repeatedly)
 * tick is in second and counted from the booting up.
 * The execution will be guaranteed even if the current time is changed.
 */
CREATE TABLE rsvs_tick (
	rsv_key INTEGER PRIMARY KEY,
	start_tick INTEGER NOT NULL, -- system tick in seconds
	duration INTEGER DEFAULT 0,  -- in seconds
	                             -- 0 if it has no duration or the duration
	                             -- cannot be determined.
	interval INTEGER DEFAULT 0,  -- seconds from start_time to next start_time.
	                             -- non-zero if it must be repeated periodically.
	                             -- next-start_tick-from-cur_tick =
	                             -- cur_tick + ((cur_tick - start_tick) % interval)
	FOREIGN KEY (rsv_key) REFERENCES reservations ON DELETE CASCADE
);

/* reservations for a program */
CREATE TABLE rsvs_program (
	rsv_key INTEGER PRIMARY KEY,
	prog_crid CHAR DEFAULT "",  -- To identify content
	                            -- May have alternatives and/or splits.
	FOREIGN KEY (rsv_key) REFERENCES reservations ON DELETE CASCADE
);

/*
 * reservations for a series recording by
 * - series CRID
 * - keyword
 */
CREATE TABLE rsvs_series (
	rsv_key INTEGER PRIMARY KEY,
	series_id CHAR NOT NULL,      -- CRID or keyword to identify series
	max_space INTEGER DEFAULT 0,  -- maximum amount of HDD space for the series
	                              -- in MB. 0 means that this series can use
	                              -- entire space of HDD partition. Non-zero
	                              -- max_space implies non-zero del_space.

	/* deletion trigger (0 value does not trigger) */
	del_day INTEGER DEFAULT 0,    -- if the content is older than N days
	del_number INTEGER DEFAULT 0, -- if the # of contents is more than N
	del_space INTEGER DEFAULT 0,  -- if the remaining space is less than N MB
	/* Trigger by del_space:
	 * If max_space is 0, triggered if remaining space in HDD partition
	 * is less than del_space.
	 * If max_space is non-zero, triggered if the value
	 * (max_space - total_amount_of_contents_in_this_series) is less
	 * than del_space.
	 */

	del_played_first INTEGER DEFAULT 0, -- when deletion is triggered,
	                                    -- delete already-played content first.

	UNIQUE (series_id),
	FOREIGN KEY (rsv_key) REFERENCES reservations ON DELETE CASCADE
);

/*
 * Schedule is a time table to execute action. -- to next N days
 */
CREATE TABLE schedules (
	sched_key INTEGER PRIMARY KEY AUTOINCREMENT,
	sched_name CHAR NOT NULL,
	description CHAR DEFAULT "",
	action INTEGER NOT NULL,     -- refer to table rsv_actions
	start_time INTEGER NOT NULL, -- unixtime, UTC
	end_time INTEGER NOT NULL,   -- unixtime, UTC
	status INTEGER DEFAULT 0,    -- 0: (in future) scheduled
	                             -- 1: (in future) running is refused by user
	                             -- 2: (in future, soon) about to run
	                             -- 3: (present) pending
	                             -- 4: (present) running
	                             -- past series schedule will not be removed
	                             -- not to record reruns.
	                             -- 5: (past) finished completely
	                             -- 6: (past) finished incompletely 
	                             -- 7: (past) finished and could not run at all

	/* for currently-running schedule */
	actual_start_time INTEGER DEFAULT 0,  -- unixtime, UTC
	running_time INTEGER DEFAULT 0,
	error INTEGER DEFAULT 0,     -- why could not be completed: can be OR-ed.
	                             -- set when it is running or finished
	                             -- 0x01: lower priority
	                             -- 0x02: interrupted by user
	                             -- 0x04: signal failure
	                             -- 0x08: insufficient storage
	                             -- 0x10: DRM restriction
	                             -- 0x20: network failure

	/* for a schedule involved in a service */
	svc_key INTEGER DEFAULT 0,

	/* for a schedule involved in an event */
	evid INTEGER DEFAULT 0,
	prog_crid CHAR DEFAULT "",        -- to identify content
	season INTEGER DEFAULT 0,
	episode INTEGER DEFAULT 0,
	total_episodes INTEGER DEFAULT 0,

	/* for a split schedule */
	imi CHAR DEFAULT "",              -- to identify split
	split_number INTEGER DEFAULT 1,
	total_splits INTEGER DEFAULT 1,

	/* The following fields should be re-evaluated whenever
	 * - schedule is added, removed, refused or changed in time.
	 * - the priority of reservation is changed.
	 * TODO: Then, do they need to be saved in DB? */
	conflict INTEGER,      -- 0: does not conflict
	                       -- non-zero: conflicts with other schedule
	                       -- 1: will run for a whole period (complete)
	                       -- 2: will run for a partial period (incomplete)
	                       -- 3: will not run at all
	start_padding INTEGER, -- in seconds
	end_padding INTEGER,   -- in seconds

	UNIQUE(action, svc_key, start_time, end_time),
	FOREIGN KEY (action) REFERENCES rsv_actions,
	FOREIGN KEY (svc_key) REFERENCES services ON DELETE CASCADE
);

/*
 * Linking table for reservations and schedules.
 * Reservation to schedule is an M:N relationship.
 *
 * 1:1 -- The simple recording like an EBR or TBR
 *   One reservation have only one schedule which is referred
 *   by that reservation only.
 *
 * 1:N -- Series, repeating or splitted reservation can have multiple schedules
 *
 * M:1 -- Duplicated schedule recording
 *   Multiple reservations may record the same event.
 *   Then, multiple reservations share one schedule.
 *   In this case, the pathname of each recording is different each other.
 *   and each recording file is hard-linked in file system.
 *   The directory to save is given by the reservation.
 *
 * 1:0 -- Some reservations may not have a schedule
 *   Many kinds of reservations that are not recording, downloading nor
 *   watching don't have any schedule. And an old series reservation that no
 *   event left to record also does not have a schedule.
 *   In this case, no row in rsv_links is made.
 *
 * 0:1 -- Instant recording (the schedule is not by reservation)
 *   In this case, the rsv_key of a row is NULL.
 */
CREATE TABLE rsv_links (
	rsv_key INTEGER,
	sched_key INTEGER,
	pathname CHAR,        -- directory + filename for recording or downloading.
	FOREIGN KEY (sched_key) REFERENCES schedules ON DELETE CASCADE,
	FOREIGN KEY (rsv_key) REFERENCES reservations ON DELETE CASCADE,
	UNIQUE (rsv_key, sched_key),
	UNIQUE (pathname)
);

/*
 * If reservation is removed, its related schedule must also be removed
 * unless the scheduled is referred by another reservations.
 * This trigger removes a schedule which is not referred by any reservation.
 */
CREATE TRIGGER remove_not_referred_schedule AFTER DELETE ON rsv_links
    WHEN (SELECT count(sched_key) from rsv_links WHERE sched_key = OLD.sched_key) IS 0
BEGIN
    DELETE FROM schedules WHERE sched_key = OLD.sched_key;
END;


/*
 * Meta data for contents (including on-going recording or downloading).
 * Created when starting recording or downloading.
 *
 * In addition, the followings must also be saved, which are not exampled here.
 * - all event and stream informations while recording
 *   * genres, parental_ratings, event texts, audio, subtitle, ...
 * - bookmarks
 *
 * On-going recordings can be related with reservations or schedules via
 * table rsv_links by pathname.
 *
 * This table can be an example to show what to save because
 * usually meta data is not saved in DB but written in HDD.
 * If the meta data is saved in HDD, saving cont_key and pathname is not
 * necessary.
 */
CREATE TABLE contents (
	cont_key INTEGER PRIMARY KEY AUTOINCREMENT,
	pathname CHAR NOT NULL,
	cont_name CHAR NOT NULL,
	description CHAR DEFAULT "",
	cont_type INTEGER NOT NULL,  -- 0 unknown
	                             -- 1 a time-shifted recording from live
	                             -- 2 a linear recording from live
	                             -- 3 a delayed-recording from HDD
	                             -- 4 a re-recording from HDD
	                             -- 5 a VOD content from network

	start_time INTEGER NOT NULL, -- unixtime, UTC
	duration INTEGER DEFAULT 0,  -- the length of content in time
	                             -- this value may be increased
	                             -- while recording or downloading
	status INTEGER DEFAULT 0,    -- 0: unknown
	                             -- 4: on-going (being recorded or downloaded)
	                             -- 5: finished completely
	                             -- 6: finished incompletely 
	                             -- 7: finished and could not run at all
	error INTEGER,               -- why failed to be completed: can be OR-ed.
	                             -- 0x01: lower priority
	                             -- 0x02: interrupted by user
	                             -- 0x04: signal failure
	                             -- 0x08: insufficient storage
	                             -- 0x10: DRM restriction
	                             -- 0x20: network failure

	/* representative service information: copied from services for the case
	 * that the service is removed after this recording is made */
	onid INTEGER,
	tsid INTEGER,
	svid INTEGER,
	svc_name CHAR,
	svc_lcn INTEGER,

	/* representative content information */
	evid INTEGER DEFAULT 0,
	prog_crid CHAR DEFAULT "",
	season INTEGER DEFAULT 0,
	episode INTEGER DEFAULT 0,
	total_episodes INTEGER DEFAULT 0,
	genre_level_1 INTEGER,
	genre_level_2 INTEGER,
	parental_rating INTEGER,
	/* collection of all events in recording should be saved, too */

	/* for a split content */
	imi CHAR DEFAULT "",              -- to identify split
	split_number INTEGER DEFAULT 1,
	total_splits INTEGER DEFAULT 1,

	/* representative stream information */
	container_type INTEGER,
	pmt_pid INTEGER,
	video_codec INTEGER,
	video_x_size INTEGER,
	video_y_size INTEGER,
	is_video_interlaced INTEGER,
	frame_per_sec INTEGER,
	audio_codec INTEGER,
	audio_sample_rate INTEGER,
	num_audio_channels INTEGER,
	has_audio_description INTEGER,
	audio_langs CHAR,        -- comma-separated string for multiple audios
	subtitle_langs CHAR,     -- comma-separated string for multiple subtitles

	/* for playing */
	is_play_locked INTEGER,
	is_deletion_locked INTEGER,
	is_hided INTEGER,
	scramble_type INTEGER,   -- non-zero if it is scrambled
	encryption_type INTEGER, -- non-zero if it is encrypted
	has_been_played_completely INTEGER,  -- boolean
	last_play_point INTEGER, -- in seconds.
	                         -- This value may be changed while playing.
	UNIQUE (pathname)
);

/*
 * meta data for directory (to contain series recordings)
 *
 * This table is just an example to show what to save because usually meta data
 * is not saved in DB but written in HDD. If the meta data is saved in HDD,
 * saving directory field is not necessary.
 *
 * The fields are copied from table reservations and rsvs_series, so, many
 * fields are duplicated.
 *
 * Duplicating fields are for the case:
 * - When factory-defaulted, reservation will be erased but directory in HDD
 *   must survive.
 * - When formatting HDD, reservation must survive.
 *
 * Care must be taken to maintain the synchronization between table
 * reservations/rsvs_series and directories.
 *
 * Series existing in DB can be related with rsvs_series and reservations
 * by (target, series_id).
 *
 * Note that rsv_key and svc_key are not saved because those keys may be
 * removed after directory and recordings are made.
 */
CREATE TABLE directories (
	directory CHAR PRIMARY KEY,   -- absolute path of the directory
	target INTEGER NOT NULL,      -- 3 a keyword
	                              -- 4 a program CRID
	                              -- 5 a series CRID
	series_id CHAR NOT NULL,      -- CRID or keyword to identify series

	deactivated INTEGER DEFAULT 0,
	dir_name CHAR NOT NULL,
	description CHAR DEFAULT "",

	preferred_onid INTEGER,
	preferred_tsid INTEGER,
	preferred_svid INTEGER,

	max_space INTEGER DEFAULT 0,  -- maximum amount of HDD space for the series
	                       -- in MB. 0 means that this series can use
	                       -- entire space of HDD partition.
	                       -- Non-zero max_space implies non-zero del_space.

	/* deletion trigger (0 value does not trigger) */
	del_day INTEGER DEFAULT 0,    -- if the content is older than N days
	del_number INTEGER DEFAULT 0, -- if the # of contents is more than N
	del_space INTEGER DEFAULT 0,  -- if the remaining space is less than N MB
	del_played_first INTEGER DEFAULT 0, -- when deletion is triggered,
	                              -- delete already-played content first.

	UNIQUE (target, series_id)
);


/***************************************************************************
                                initial values
 ***************************************************************************/

/*
 * pre-defined entries for special purpose
 */
INSERT INTO networks (nid, net_name) VALUES (0, "unknown network");
INSERT INTO sources (src_key, delivery_system, src_name) VALUES (0, 9, "unknown source");
INSERT INTO operators (op_key, op_name) VALUES (0, "unknown operator");
INSERT INTO transports (ts_key, nid, tsid, onid, src_key, op_key) VALUES (0, 0, 0, 0, 0, 0);
INSERT INTO services (svc_key, ts_key, svid, type, svc_name, prov_name) VALUES (0, 0, 0, 0, "<void service>", "<special use only>");


/*
 * known sources
 */
INSERT INTO sources (delivery_system, src_name, description) VALUES (8, "~/Videos/TS", "TS files for test");
INSERT INTO sources (delivery_system, src_name, description) VALUES (8, "~/Videos/TS2", "TS files for test 2");
INSERT INTO sources (delivery_system, src_name) VALUES (2, "UK");
INSERT INTO sources (delivery_system, src_name) VALUES (2, "Sweden");
INSERT INTO sources (delivery_system, src_name) VALUES (2, "Australia");
INSERT INTO sources (delivery_system, src_name) VALUES (2, "TEST-TER");
INSERT INTO sources (delivery_system, src_name) VALUES (1, "Primacom");
INSERT INTO sources (delivery_system, src_name, orbital_position, description) VALUES (0, "Astra 19.2E", 192, "Astra 19.2E fleet");
INSERT INTO sources (delivery_system, src_name, orbital_position, description) VALUES (0, "Astra 28.2E", 282, "Astra 28.2E fleet");
INSERT INTO sources (delivery_system, src_name, orbital_position, description) VALUES (0, "Optus 156.0E", 1560, "Optus C1/D3 (Austrailia Satellite)");
INSERT INTO sources (delivery_system, src_name, orbital_position) VALUES (0, "JCSAT 3A", 1280);
INSERT INTO sources (delivery_system, src_name, orbital_position) VALUES (0, "JCSAT 4A", 1240);
INSERT INTO sources (delivery_system, src_name, orbital_position) VALUES (0, "AsiaSAT 3S", 1055);
INSERT INTO sources (delivery_system, src_name, orbital_position) VALUES (0, "AsiaSAT 5", 1005);
INSERT INTO sources (delivery_system, src_name) VALUES (0, "TEST-LNB-OFF");
INSERT INTO sources (delivery_system, src_name) VALUES (0, "TEST-LNB-ON");
INSERT INTO sources (delivery_system, src_name) VALUES (0, "TEST-A-OFF");
INSERT INTO sources (delivery_system, src_name) VALUES (0, "TEST-A-ON");
INSERT INTO sources (delivery_system, src_name) VALUES (0, "TEST-B-OFF");
INSERT INTO sources (delivery_system, src_name) VALUES (0, "TEST-B-ON");
INSERT INTO sources (delivery_system, src_name) VALUES (0, "TEST-C-OFF");
INSERT INTO sources (delivery_system, src_name) VALUES (0, "TEST-C-ON");
INSERT INTO sources (delivery_system, src_name) VALUES (0, "TEST-D-OFF");
INSERT INTO sources (delivery_system, src_name) VALUES (0, "TEST-D-ON");


/***************************************************************************
                            initial reservations
 ***************************************************************************/

/*
 * Turn on if it is in standby mode to do daily jobs on every 4:30 AM.
 * day_of_week value 127 means everyday (0x7f).
 * 
 * If it is in standby mode on 4:30 AM, it will be turned on and
 * enter into standby mode again. While entering into standby,
 * some other reservations will be executed.
 * If it is in operation mode on 4:30, nothings will be done.
 */
INSERT INTO reservations (rsv_name, action, do_when, replan_when)
	VALUES ("Daily Jobs", 1, 1, (8|128));
INSERT INTO rsvs_daily (rsv_key, hhmmss, day_of_week)
	VALUES (last_insert_rowid(), 43000, 127);

/*
 * The reservations that will be executed when entering into standby mode.
 */

/* update channel list */
INSERT INTO reservations (rsv_name, action, do_when)
	VALUES ("Quasi-static update", 12, 3);

/* update S/W */
INSERT INTO reservations (rsv_name, action, do_when)
	VALUES ("OTA in standby", 14, 3);

/* collect EIT -- will be stopped when completing */
INSERT INTO reservations (rsv_name, action, do_when, replan_when)
	VALUES ("Collect EIT standby", 13, 3, 16);

/*
 * The reservations that will be executed when entering into operation mode.
 */

/* the initial channel -- svc_key will be updated on every channel change */
INSERT INTO reservations (rsv_name, action, target, svc_key, do_when, replan_when)
	VALUES ("initial channel to watch", 10, 1, 0, 4, 32);

/* collect EIT -- will be stopped when exiting from operation mode */
INSERT INTO reservations (rsv_name, action, do_when, replan_when)
	VALUES ("Collect EIT operation", 13, 4, 2);

/* update S/W -- will be restarted on every tuning
 * and will be stopped when exiting from operation mode */
INSERT INTO reservations (rsv_name, action, do_when, replan_when)
	VALUES ("OTA in live", 14, 4, (2|64));


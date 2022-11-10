/***************************************************************************
                      schema to contain event information
 ***************************************************************************/

PRAGMA foreign_keys = ON;

CREATE TABLE events (
	evt_key INTEGER PRIMARY KEY AUTOINCREMENT,
	svc_key INTEGER,
	evid INTEGER,
	start_time INTEGER,      -- unixtime, UTC
	end_time INTEGER,        -- unixtime, UTC
	version_number INTEGER,  -- version_number of section table
	                         -- containing this event
	-- FOREIGN KEY (svc_key) REFERENCES services ON DELETE CASCADE,
	UNIQUE (svc_key, evid)  -- event is also identified by these two values
);
CREATE INDEX event_start_time ON events (start_time);

/* nibbles in content_descriptor */
CREATE TABLE event_genres (
	evt_key INTEGER,    -- evt_key is not a primary key because
	                    -- there may be multiple records for an evt_key.
	level_1 INTEGER,
	level_2 INTEGER,
	user_byte INTEGER,
	FOREIGN KEY (evt_key) REFERENCES events ON DELETE CASCADE
);
CREATE INDEX event_genres_index ON event_genres (evt_key);

CREATE TABLE event_texts (
	evt_key INTEGER,    -- evt_key is not a primary key because
	                    -- there may be multiple records for an evt_key.
	lang CHAR,
	evt_name CHAR,      -- event_name in short_event_descriptor
	short_text CHAR,    -- text in short_event_descriptor
	extended_text CHAR, -- text in extended_event_descriptor
	FOREIGN KEY (evt_key) REFERENCES events ON DELETE CASCADE
);
CREATE INDEX event_texts_index ON event_texts (evt_key);

CREATE TABLE event_parental_ratings (
	evt_key INTEGER,    -- evt_key is not a primary key because
	                    -- there may be multiple records for an evt_key.
	country_code CHAR,
	rating INTEGER,
	FOREIGN KEY (evt_key) REFERENCES events ON DELETE CASCADE
);
CREATE INDEX event_parental_ratings_index ON event_parental_ratings (evt_key);

/* event items in extended_event_descriptor */
CREATE TABLE event_items (
	evt_key INTEGER,    -- evt_key is not a primary key because
	                    -- there may be multiple records for an evt_key.
	lang CHAR,
	item_desc CHAR,
	item CHAR,
	FOREIGN KEY (evt_key) REFERENCES events ON DELETE CASCADE
);
CREATE INDEX event_item_index ON event_items (evt_key);

CREATE TABLE series_crids (
	evt_key INTEGER,    -- evt_key is not a primary key because
	                    -- there may be multiple records for an evt_key.
	series_crid CHAR,
	FOREIGN KEY (evt_key) REFERENCES events ON DELETE CASCADE
);
CREATE INDEX series_crid_evt_index ON series_crids (evt_key);
CREATE INDEX series_crid_index ON series_crids (series_crid);

CREATE TABLE programs (
	evt_key INTEGER PRIMARY KEY,
	prog_crid CHAR,     -- program CRID: authority + data
	imi CHAR,           -- program CRID: IMI field
	season INTEGER,
	episode INTEGER,
	total_episodes INTEGER,
	FOREIGN KEY (evt_key) REFERENCES events ON DELETE CASCADE
);
CREATE INDEX program_crid_index ON programs (prog_crid);


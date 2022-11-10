/***************************************************************************
                  schema to contain preferences and settings
 ***************************************************************************/

/*
 * for multi-user profile
 */
CREATE TABLE users (
	user_key INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT,
	description TEXT
);

CREATE TABLE settings (
	user_key INTEGER NOT NULL,
	name TEXT PRIMARY KEY,
	value TEXT,   -- CAUTION: integer value must be saved as a string
	FOREIGN KEY (user_key) REFERENCES users ON DELETE CASCADE
);

/***************************************************************************
                            initial values
 ***************************************************************************/

INSERT INTO users (user_key, username, description) VALUES (0, "all users", "all users");

INSERT INTO settings (user_key, name, value) SELECT user_key, "parental_rating", "18" FROM users WHERE username = "default user";
INSERT INTO settings (user_key, name, value) SELECT user_key, "start_padding", "300" FROM users WHERE username = "default user";
INSERT INTO settings (user_key, name, value) SELECT user_key, "end_padding", "300" FROM users WHERE username = "default user";


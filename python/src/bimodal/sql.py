CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS site (
    site_id INTEGER PRIMARY KEY NOT NULL,
    site_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS count (
    count_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    site_name TEXT NOT NULL,
    record_time TEXT NOT NULL,
    count_incoming INTEGER,
    count_outgoing INTEGER,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    hour INTEGER NOT NULL,
    weekday INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS wind (
    wind_record_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    record_time TEXT NOT NULL,
    direction_deg INTEGER,
    speed_ms FLOAT NOT NULL,
    direction_std FLOAT,
    speed_std FLOAT,
    period FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS rain (
    rain_record_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    record_time TEXT NOT NULL,
    amount FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS temperature (
    temperature_record_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    record_time TEXT NOT NULL,
    temp_max_c FLOAT,
    temp_min_c FLOAT,
    temp_avg_c FLOAT,
    rel_humidity_perc INTEGER
);
"""


INSERT_SITE = """
INSERT INTO site (site_id, site_name) VALUES (?, ?)
"""

INSERT_COUNT = """
INSERT INTO count
(
    site_name,
    record_time,
    count_incoming,
    count_outgoing,
    year,
    month,
    day,
    hour,
    weekday
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

INSERT_WIND = """
INSERT INTO wind
(
    record_time,
    direction_deg,
    speed_ms,
    direction_std,
    speed_std,
    period
) VALUES (?, ?, ?, ?, ?, ?)
"""

INSERT_RAIN = """
INSERT INTO rain
(
    record_time,
    amount
) VALUES (?, ?)
"""

INSERT_TEMPERATURE = """
INSERT INTO temperature
(
    record_time,
    temp_max_c,
    temp_min_c,
    temp_avg_c,
    rel_humidity_perc
) VALUES (?, ?, ?, ?, ?)
"""

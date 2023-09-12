SQL_CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS site (
    site_id INTEGER PRIMARY KEY NOT NULL,
    site_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS count (
    count_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    site_name TEXT NOT NULL,
    rec_time TEXT NOT NULL,
    count_incoming INTEGER,
    count_outgoing INTEGER
);
"""


SQL_INSERT_SITE = """
INSERT INTO site (site_id, site_name) VALUES (?, ?)
"""

SQL_INSERT_COUNT = """
INSERT INTO count 
(site_name, rec_time, count_incoming, count_outgoing) VALUES (?, ?, ?, ?)
"""

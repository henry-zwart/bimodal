from __future__ import annotations
from pathlib import Path

from .sql import SQL_CREATE_TABLES, SQL_INSERT_SITE, SQL_INSERT_COUNT

import sqlite3
import polars as pl


class DatabaseError(Exception):
    ...


class Database:
    def __init__(self, path: Path):
        self.path = path
        if not self.path.exists():
            raise DatabaseError("Database not initialised")

    @staticmethod
    def initialise(path: Path) -> Database:
        if not path.exists():
            path.mkdir()

        with sqlite3.connect(path / Path("db.sqlite")) as conn:
            conn.executescript(SQL_CREATE_TABLES)
            conn.commit()

        return Database(path / Path("db.sqlite"))

    def build_from(self, df: pl.DataFrame):
        self.add_sites(df)
        self.add_counts(df)

    def add_sites(self, df: pl.DataFrame):
        with sqlite3.connect(self.path) as conn:
            conn.executemany(
                SQL_INSERT_SITE,
                (
                    df.drop(["record_time", "count_incoming", "count_outgoing"])
                    .unique()
                    .rows()
                ),
            )

    def add_counts(self, df: pl.DataFrame):
        with sqlite3.connect(self.path) as conn:
            conn.executemany(SQL_INSERT_COUNT, df.drop("site_id").rows())

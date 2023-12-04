from __future__ import annotations

import sqlite3
from pathlib import Path

import polars as pl

from bimodal.config import WEATHER_TYPES

from . import sql


class DatabaseError(Exception):
    ...


class Database:
    def __init__(self, path: Path):
        self.path = path
        if not self.path.exists():
            raise DatabaseError("Database not initialised")

    @staticmethod
    def create(path: Path) -> Database:
        if not path.exists():
            path.mkdir()

        if (path / "db.sqlite").exists():
            (path / "db.sqlite").unlink()

        with sqlite3.connect(path / Path("db.sqlite")) as conn:
            conn.executescript(sql.CREATE_TABLES)
            conn.commit()

        return Database(path / Path("db.sqlite"))

    def build_from(self, path: Path):
        count_data = pl.read_parquet(path / "counter_data.parquet")
        self.add_sites(count_data)
        self.add_counts(count_data)
        self.add_weather_data(path)

    def add_sites(self, df: pl.DataFrame):
        with sqlite3.connect(self.path) as conn:
            conn.executemany(
                sql.INSERT_SITE,
                (df.select("site_id", "site_name").unique().rows()),
            )

    def add_counts(self, df: pl.DataFrame):
        with sqlite3.connect(self.path) as conn:
            conn.executemany(sql.INSERT_COUNT, df.drop("site_id").rows())

    def add_weather_data(self, data_dir: Path):
        for weather_type in WEATHER_TYPES:
            match weather_type:
                case "rain":
                    script = sql.INSERT_RAIN
                case "wind":
                    script = sql.INSERT_WIND
                case "temp":
                    script = sql.INSERT_TEMPERATURE
                case _:
                    raise ValueError("Huh?")
            df = pl.read_parquet(data_dir / f"weather_{weather_type}.parquet")
            with sqlite3.connect(self.path) as conn:
                conn.executemany(script, df.rows())

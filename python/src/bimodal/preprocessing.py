import datetime
from pathlib import Path

import polars as pl

from . import config


def preprocess_counter_data(source: Path, save_dir: Path):
    dfs = []
    for fp in source.glob("*.csv"):
        data = pl.read_csv(fp).with_columns(pl.col("^.* count$").cast(pl.Int64))
        incoming_data = (
            data.filter(
                (pl.col("Incoming count").is_not_null())
                & (pl.col("Outgoing count") == 0)
            )
            .drop("Outgoing count")
            .lazy()
            .groupby(["Site ID", "Site name", "Date/time"])
            .max()
            .collect()
        )
        outgoing_data = (
            data.filter(
                (pl.col("Outgoing count").is_not_null())
                & (pl.col("Incoming count") == 0)
            )
            .drop("Incoming count")
            .lazy()
            .groupby(["Site ID", "Site name", "Date/time"])
            .max()
            .collect()
        )
        cleaned = (
            data.drop("Incoming count", "Outgoing count")
            .unique(maintain_order=True)
            .join(incoming_data, on=["Site ID", "Site name", "Date/time"], how="left")
            .join(outgoing_data, on=["Site ID", "Site name", "Date/time"], how="left")
            .rename(config.COUNTER_RENAME_MAPPING)
        )
        dfs.append(cleaned)
    (
        pl.concat(dfs)
        .with_columns(
            pl.col("record_time").str.to_datetime() + datetime.timedelta(hours=1)
        )
        .with_columns(
            pl.col("record_time").dt.year().alias("year"),
            pl.col("record_time").dt.month().alias("month"),
            pl.col("record_time").dt.day().alias("day"),
            pl.col("record_time").dt.hour().alias("hour"),
            pl.col("record_time").dt.weekday().alias("weekday"),
        )
        .sort(by=[pl.col("site_name"), pl.col("record_time")])
    ).write_parquet(save_dir / "counter_data.parquet")


def split_weather_file(filepath: Path):
    if not filepath.exists():
        raise FileExistsError

    with filepath.open("r") as f:
        i = -1
        buff = []
        while line := f.readline():
            if line == "\n":
                if i >= 0:
                    new_path = (
                        filepath.parent
                        / f"{filepath.stem}-{config.WEATHER_TYPES[i]}.csv"
                    )
                    with new_path.open("w") as nf:
                        nf.writelines(buff[1:])
                buff = []
                i += 1
            else:
                buff.append(line)


def join_biannual_split_weather_files(directory: Path):
    dfs = {}

    for weather_type in config.WEATHER_TYPES:
        df = (
            pl.concat(
                [
                    pl.read_csv(
                        p,
                        null_values=["-"],
                        dtypes={"Period(Hrs)": pl.Float64},
                        try_parse_dates=True,
                    )
                    for p in directory.glob(f"*-{weather_type}.csv")
                ]
            )
            .with_columns(pl.col("Date(NZST)").str.to_datetime("%Y%m%d:%H%M"))
            .sort(by=pl.col("Date(NZST)"))
        )
        dfs[weather_type] = df

    return dfs


def preprocess_weather_data(from_dir: Path, save_dir: Path):
    for p in from_dir.glob("weather-*"):
        split_weather_file(p)

    dfs = join_biannual_split_weather_files(from_dir)
    for weather_type, df in dfs.items():
        df = (
            df.drop(config.WEATHER_DROP_COLS[weather_type])
            .rename(config.WEATHER_RENAME_MAPPING[weather_type])
            .with_columns(
                pl.col("record_time").dt.year().alias("year"),
                pl.col("record_time").dt.month().alias("month"),
                pl.col("record_time").dt.day().alias("day"),
                pl.col("record_time").dt.hour().alias("hour"),
            )
        )
        df.write_parquet(save_dir / f"weather_{weather_type}.parquet")

    # clean up interim csvs
    for weather_type in config.WEATHER_TYPES:
        for p in (from_dir).glob(f"*-{weather_type}.csv"):
            p.unlink()

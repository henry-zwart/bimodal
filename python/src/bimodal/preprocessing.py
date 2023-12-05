from pathlib import Path

import holidays
import polars as pl

from . import config


def preprocess_holidays(save_dir: Path):
    welly_holidays = holidays.NZ(
        years=[2018, 2019, 2020, 2021, 2022, 2023], subdiv="WGN"
    )
    (
        pl.DataFrame(
            {"date": welly_holidays.keys(), "holiday_name": welly_holidays.values()}
        )
    ).write_parquet(save_dir / "wellington_holidays.parquet")


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
            pl.col("record_time")
            .str.to_datetime()
            .dt.replace_time_zone(None)  # + datetime.timedelta(hours=1)
        )
        .with_columns(
            pl.col("record_time").dt.year().alias("year"),
            (pl.col("record_time").dt.month() - 1).alias("month"),
            pl.col("record_time").dt.day().alias("day"),
            pl.col("record_time").dt.hour().alias("hour"),
            (pl.col("record_time").dt.weekday() - 1).alias("weekday"),
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


def join_split_weather_files(directory: Path):
    """
    Loads individual-year files and concatenates.

    NIWA datetimes are different to how we expect. They refer to the datetime at the end
    of an observation period, and also include the 0th hour of the year + the 0th hour
    of the next year. We modify this to fit our expected format (used by the bike
    counts), by:

        1. Decrementing each datetime by 1 hour
        2. Dropping the first observation (which refers to the last observation of the
            previous year)
    """

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
                    .with_columns(
                        pl.col("Date(NZST)")
                        .str.to_datetime("%Y%m%d:%H%M")
                        .dt.offset_by("-1h")
                    )
                    .sort(by=pl.col("Date(NZST)"))
                    .tail(-1)
                    for p in directory.glob(f"*-{weather_type}.csv")
                ]
            )
            # .with_columns(pl.col("Date(NZST)").str.to_datetime("%Y%m%d:%H%M"))
            .sort(by=pl.col("Date(NZST)"))
        )
        dfs[weather_type] = df

    return dfs


def preprocess_weather_data(from_dir: Path, save_dir: Path):
    for p in from_dir.glob("weather-*"):
        split_weather_file(p)

    dfs = join_split_weather_files(from_dir)
    for weather_type, df in dfs.items():
        df = df.drop(config.WEATHER_DROP_COLS[weather_type]).rename(
            config.WEATHER_RENAME_MAPPING[weather_type]
        )
        df.write_parquet(save_dir / f"weather_{weather_type}.parquet")

    # clean up interim csvs
    for weather_type in config.WEATHER_TYPES:
        for p in (from_dir).glob(f"*-{weather_type}.csv"):
            p.unlink()

from pathlib import Path

import polars as pl

from bimodal import config


def load_count_data(assets_path: Path) -> pl.DataFrame:
    """Load df of incoming and outgoing count data from different locations."""
    return pl.read_parquet(f"{assets_path}/counter_data.parquet")


def load_combined_weather_data(assets_path: Path) -> pl.DataFrame:
    """Load separate weather dfs and combine, renaming cols and dropping some."""
    wind_df = pl.read_parquet(f"{assets_path}/weather_wind.parquet")
    rain_df = pl.read_parquet(f"{assets_path}/weather_rain.parquet")
    temperature_df = pl.read_parquet(f"{assets_path}/weather_temp.parquet")
    return (
        wind_df.join(rain_df, on="record_time", how="left")
        .join(temperature_df, on="record_time", how="left")
        .rename(
            {
                "speed_ms": "wind_speed",
                "dir_deg": "wind_direction",
                "speed_std": "wind_speed_std",
                "amount": "rainfall",
                "temp_avg_c": "average_temperature",
                "temp_min_c": "min_temperature",
                "temp_max_c": "max_temperature",
            }
        )
        .drop("dir_std", "period", "rel_humidity_perc")
    )


def load_holidays_data(assets_path: Path) -> pl.DataFrame:
    """Load df of NZ holidays (date, name)"""
    return pl.read_parquet(f"{assets_path}/wellington_holidays.parquet")


def get_combined_hourly_counts_and_weather(assets_path: Path) -> pl.DataFrame:
    count_df = load_count_data(assets_path)
    weather_df = load_combined_weather_data(assets_path)
    holidays_df = load_holidays_data(assets_path)

    return (
        count_df.join(weather_df, on="record_time", how="left")
        .with_columns(pl.col("record_time").dt.date().alias("date"))
        .join(holidays_df, on="date", how="left")
        .with_columns(
            pl.when(pl.col("holiday_name").is_not_null())
            .then(1)
            .otherwise(0)
            .alias("is_holiday"),
            (
                (
                    pl.col("record_time").dt.date().first() - config.INITIAL_DATE
                ).dt.days()
                / 365.25
            ).alias("time_in_years"),
        )
        .drop("date")
    )


def create_hourly_counts_dataset(assets_path: Path):
    hourly_counts_dataset = get_combined_hourly_counts_and_weather(assets_path)

    # Reorganise columns
    hourly_counts_dataset = hourly_counts_dataset.select(
        "site_name",
        "record_time",
        "year",
        "month",
        "day",
        "hour",
        "weekday",
        "is_holiday",
        "holiday_name",
        "time_in_years",
        "count_incoming",
        "count_outgoing",
        "wind_speed",
        "wind_speed_std",
        "wind_direction",
        "rainfall",
        "average_temperature",
        "max_temperature",
        "min_temperature",
    )
    hourly_counts_dataset.write_parquet(f"{assets_path}/dataset_hourly_counts.parquet")


def create_daily_counts_dataset(assets_path: Path):
    hourly_counts_dataset = get_combined_hourly_counts_and_weather(assets_path)
    daily_counts_dataset = hourly_counts_dataset.group_by(
        pl.col("site_name"),
        pl.col("year"),
        pl.col("month"),
        pl.col("day"),
        maintain_order=True,
    ).agg(
        pl.col("record_time").dt.date().first().alias("date"),
        pl.col("weekday").first(),
        pl.col("is_holiday").first(),
        pl.col("holiday_name").first(),
        (
            (pl.col("record_time").dt.date().first() - config.INITIAL_DATE).dt.days()
            / 365.25
        ).alias("time_in_years"),
        pl.col("count_outgoing").sum(),
        pl.col("count_incoming").sum(),
        pl.col("rainfall").sum().alias("total_rainfall"),
        pl.col("wind_speed").median().alias("median_wind_speed"),
        pl.col("average_temperature").mean(),
    )

    # Reorganise columns
    daily_counts_dataset = daily_counts_dataset.select(
        "site_name",
        "date",
        "year",
        "month",
        "day",
        "weekday",
        "is_holiday",
        "holiday_name",
        "time_in_years",
        "count_incoming",
        "count_outgoing",
        "median_wind_speed",
        "total_rainfall",
        "average_temperature",
    )
    daily_counts_dataset.write_parquet(f"{assets_path}/dataset_daily_counts.parquet")

from pathlib import Path
from typing import Annotated

import typer
from typer import Argument

from . import config, datasets, preprocessing
from .database import Database

app = typer.Typer(
    add_completion=True,
    no_args_is_help=True,
    help="Analysis of bike count data from Wellington.",
)


@app.command(help="Preprocess counter and weather data")
def preprocess_data():
    preprocessing.preprocess_counter_data(
        config.RAW_DATA_PATH / "counter", config.CLEAN_DATA_PATH
    )
    preprocessing.preprocess_weather_data(
        config.RAW_DATA_PATH / "weather", config.CLEAN_DATA_PATH
    )
    preprocessing.preprocess_holidays(config.CLEAN_DATA_PATH)


@app.command()
def build_db(
    assets_path: Annotated[
        Path,
        Argument(
            help="Path to preprocessed assets. Database created in same location."
        ),
    ]
):
    """Creates sqlite database from preprocessed data."""
    db = Database.create(assets_path)
    db.build_from(assets_path)


@app.command()
def build_datasets(
    assets_path: Annotated[
        Path,
        Argument(
            help="Path to preprocessed assets. Datasets created in same location."
        ),
    ]
):
    """Creates dataset parquets with combination of count, weather, etc."""
    datasets.create_hourly_counts_dataset(assets_path)
    datasets.create_daily_counts_dataset(assets_path)

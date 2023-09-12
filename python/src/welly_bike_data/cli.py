from pathlib import Path
from typing import Annotated

import typer
from typer import Argument, Option

from .build.data import load_and_clean_raw
from .build.database import Database

app = typer.Typer(
    add_completion=True,
    no_args_is_help=True,
    help="Analysis of bike count data from Wellington.",
)

RAW_DATA_PATH = Path("data/raw_counter")

YEAR_FILES = {
    2018: Path("2018_ecocounter_data_20230905140019.csv"),
    2019: Path("2019_ecocounter_data_20230905140408.csv"),
    2020: Path("2020_ecocounter_data_20230905140803.csv"),
    2021: Path("2021_ecocounter_data_20230905141200.csv"),
    2022: Path("2022_ecocounter_data_20230905141557.csv"),
    2023: Path("2023_ecocounter_data_20230905141951.csv"),
}


@app.command()
def build_db(db_path: Annotated[Path, Argument(help="Path for new sqlite db")]):
    """Cleans raw data and stores in a SQLITE database."""
    df = load_and_clean_raw([RAW_DATA_PATH / yf for yf in YEAR_FILES.values()])
    db = Database.initialise(db_path)
    db.build_from(df)

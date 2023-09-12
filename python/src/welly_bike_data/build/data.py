from pathlib import Path
import polars as pl

RENAME_MAPPING = {
    "Site ID": "site_id",
    "Site name": "site_name",
    "Date/time": "record_time",
    "Incoming count": "count_incoming",
    "Outgoing count": "count_outgoing",
}


def load_and_clean_raw(filepaths: list[Path]) -> pl.DataFrame:
    dfs = []
    for fp in filepaths:
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
            .rename(RENAME_MAPPING)
        )
        dfs.append(cleaned)
    return pl.concat(dfs)

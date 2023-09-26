from pathlib import Path

RAW_DATA_PATH = Path("data/raw")
CLEAN_DATA_PATH = Path("data")

COUNTER_RENAME_MAPPING = {
    "Site ID": "site_id",
    "Site name": "site_name",
    "Date/time": "record_time",
    "Incoming count": "count_incoming",
    "Outgoing count": "count_outgoing",
}

WEATHER_TYPES = ["wind", "rain", "temp"]

WEATHER_DROP_COLS = {
    "wind": ["Station", "Freq"],
    "rain": ["Station", "SofG", "Deficit(mm)", "Runoff(mm)", "Period(Hrs)", "Freq"],
    "temp": [
        "Station",
        "Period(Hrs)",
        "Period(Hrs)_duplicated_0",
        "Tgmin(C)",
        "Period(Hrs)_duplicated_1",
        "Period(Hrs)_duplicated_2",
        "Freq",
    ],
}

WEATHER_RENAME_MAPPING = {
    "wind": {
        "Date(NZST)": "record_time",
        "Dir(DegT)": "dir_deg",
        "Speed(m/s)": "speed_ms",
        "Dir StdDev": "dir_std",
        "Spd StdDev": "speed_std",
        "Period(Hrs)": "period",
    },
    "rain": {
        "Date(NZST)": "record_time",
        "Amount(mm)": "amount",
    },
    "temp": {
        "Date(NZST)": "record_time",
        "Tmax(C)": "temp_max_c",
        "Tmin(C)": "temp_min_c",
        "Tmean(C)": "temp_avg_c",
        "RHmean(%)": "rel_humidity_perc",
    },
}

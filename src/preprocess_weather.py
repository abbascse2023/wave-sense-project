import pandas as pd
import numpy as np
import re
from pathlib import Path

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
CLEANED = Path(__file__).resolve().parents[1] / "data" / "cleaned"

DROP_COLS = ["Unnamed: 4", "Unnamed: 6", "Unnamed: 8", "Unnamed: 10", "Unnamed: 12", "Unnamed: 14"]

# columns we will use for model + alert
NUM_COLS = ["TEMP","DEWP","SLP","STP","VISIB","WDSP","MXSPD","GUST","MAX","MIN","PRCP","SNDP"]
KEY_COLS = ["TEMP", "WDSP", "PRCP"]  # keep it minimal so we don't drop everything

def clean_numeric_series(s: pd.Series) -> pd.Series:
    """
    NOAA GSOD often has flags like '*' or letters. Keep only digits, minus, dot.
    """
    s = s.astype(str).str.strip()
    # keep digits, minus, dot only
    s = s.str.replace(r"[^0-9\.\-]+", "", regex=True)
    s = s.replace("", np.nan)
    return pd.to_numeric(s, errors="coerce")

def main():
    CLEANED.mkdir(parents=True, exist_ok=True)

    file_path = RAW / "weather_2020_small.csv"
    print("Reading from:", file_path)

    df = pd.read_csv(file_path)
    print("Initial shape:", df.shape)

    df = df.drop(columns=[c for c in DROP_COLS if c in df.columns], errors="ignore")

    # Clean numeric cols
    for col in NUM_COLS:
        if col in df.columns:
            df[col] = clean_numeric_series(df[col])

    # FRSHTT is special: it can be 6-digit code; treat as string -> int if possible
    if "FRSHTT" in df.columns:
        df["FRSHTT"] = df["FRSHTT"].astype(str).str.replace(r"[^0-9]+", "", regex=True)
        df["FRSHTT"] = pd.to_numeric(df["FRSHTT"], errors="coerce").fillna(0).astype(int)

    # Replace typical missing codes AFTER cleaning
    missing_codes = [9999.9, 999.9, 99.99, 999.99, 999.0, 99.9]
    for col in NUM_COLS:
        if col in df.columns:
            df[col] = df[col].replace(missing_codes, np.nan)

    # drop rows that miss only key cols
    df = df.dropna(subset=[c for c in KEY_COLS if c in df.columns])
    df = df.drop_duplicates()

    print("After robust cleaning:", df.shape)

    # Create alert label (rain OR strong wind OR any hazard flag)
    # Use MXSPD if GUST is missing
    gust_col = "GUST" if "GUST" in df.columns else "MXSPD"

    df["weather_alert"] = (
        (df["PRCP"] > 0.0) |
        (df[gust_col] >= 25) |
        (df["FRSHTT"] > 0)
    ).astype(int)

    out = CLEANED / "weather_cleaned.csv"
    df.to_csv(out, index=False)
    print("Saved:", out)
    print("Alert distribution:\n", df["weather_alert"].value_counts(dropna=False))

    # Extra debug (super useful)
    print("\nSample rows (TEMP, WDSP, PRCP, GUST/MXSPD, FRSHTT):")
    show_cols = [c for c in ["TEMP","WDSP","PRCP",gust_col,"FRSHTT"] if c in df.columns]
    print(df[show_cols].head(5))

if __name__ == "__main__":
    main()

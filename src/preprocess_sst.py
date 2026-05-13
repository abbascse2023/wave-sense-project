import pandas as pd
from pathlib import Path

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
CLEANED = Path(__file__).resolve().parents[1] / "data" / "cleaned"

def main():
    CLEANED.mkdir(parents=True, exist_ok=True)

    file_path = RAW / "sst_easy.csv"
    print("Reading from:", file_path)

    df = pd.read_csv(file_path)
    print("SST initial shape:", df.shape)

    df = df.drop_duplicates().dropna()

    # Convert any temperature-like column to numeric
    for col in df.columns:
        if "temp" in col.lower():
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna()
    print("SST cleaned shape:", df.shape)

    out_path = CLEANED / "sst_cleaned.csv"
    df.to_csv(out_path, index=False)
    print("Saved cleaned file to:", out_path)

if __name__ == "__main__":
    main()

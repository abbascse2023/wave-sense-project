import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
import joblib

CLEANED = Path(__file__).resolve().parents[1] / "data" / "cleaned"
MODELS = Path(__file__).resolve().parents[1] / "models"

def main():
    MODELS.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(CLEANED / "weather_cleaned.csv")
    print("Loaded weather_cleaned:", df.shape)

    # Drop ID columns
    drop_cols = ["STN---", "WBAN", "YEARMODA"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    # Target
    y = df["weather_alert"]

    # Remove leakage columns
    leak_cols = ["weather_alert", "PRCP", "GUST", "FRSHTT"]
    X = df.drop(columns=[c for c in leak_cols if c in df.columns])

    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("\nAccuracy:", round(accuracy_score(y_test, y_pred), 4))
    print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    out_path = MODELS / "weather_alert_model.pkl"
    joblib.dump(model, out_path)

    print("\nModel saved to:", out_path)

if __name__ == "__main__":
    main()

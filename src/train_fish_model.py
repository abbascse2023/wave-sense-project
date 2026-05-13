import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

CLEANED = Path(__file__).resolve().parents[1] / "data" / "cleaned"
MODELS = Path(__file__).resolve().parents[1] / "models"

def main():
    MODELS.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(CLEANED / "sonar_cleaned.csv")
    print("Loaded sonar_cleaned:", df.shape)

    # Most sonar datasets have the label in the last column
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=3000))
    ])

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print("\nAccuracy:", round(acc, 4))
    print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    out_path = MODELS / "fish_presence_model.pkl"
    joblib.dump(model, out_path)
    print("\nSaved model to:", out_path)

if __name__ == "__main__":
    main()

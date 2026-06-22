import os
import json
import re
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

BASE = os.path.dirname(__file__)
DATASET_PATH = os.path.join(BASE, "dataset", "emails.csv")
MODELS_DIR = os.path.join(BASE, "models")
MODEL_OUT = os.path.join(MODELS_DIR, "phishing_model.pkl")
VECT_OUT = os.path.join(MODELS_DIR, "vectorizer.pkl")
METRICS_OUT = os.path.join(MODELS_DIR, "metrics.json")


def clean_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = s.lower()
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def train_and_save(dataset_path: str = None):
    dataset_path = dataset_path or DATASET_PATH
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    df = pd.read_csv(dataset_path)
    if "email_text" not in df.columns or "label" not in df.columns:
        raise ValueError("CSV must contain 'email_text' and 'label' columns")

    df = df.dropna(subset=["email_text", "label"]).reset_index(drop=True)
    df["text_clean"] = df["email_text"].astype(str).apply(clean_text)

    X_text = df["text_clean"].tolist()
    y = df["label"].astype(int).values

    vect = TfidfVectorizer(max_features=20000, ngram_range=(1, 2), stop_words="english")
    X = vect.fit_transform(X_text)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]

    cm = confusion_matrix(y_test, y_pred).tolist()
    feature_names = vect.get_feature_names_out()
    importances = clf.feature_importances_
    top_indices = np.argsort(importances)[::-1][:10]
    top_features = [
        {"feature": feature_names[int(i)], "importance": float(importances[int(i)])}
        for i in top_indices
    ]

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_proba)) if len(np.unique(y_test)) > 1 else None,
        "confusion_matrix": cm,
        "top_features": top_features,
    }

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(clf, MODEL_OUT)
    joblib.dump(vect, VECT_OUT)
    with open(METRICS_OUT, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("Training complete. Model and vectorizer saved.")
    print(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    train_and_save()

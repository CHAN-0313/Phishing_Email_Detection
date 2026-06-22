import os
import joblib
import json
from typing import Tuple
from feature_extractor import extract_features

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "phishing_model.pkl")
VECT_PATH = os.path.join(os.path.dirname(__file__), "models", "vectorizer.pkl")
METRICS_PATH = os.path.join(os.path.dirname(__file__), "models", "metrics.json")


def load_artifacts():
    model = None
    vect = None
    metrics = {}
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
    if os.path.exists(VECT_PATH):
        vect = joblib.load(VECT_PATH)
    if os.path.exists(METRICS_PATH):
        try:
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                metrics = json.load(f)
        except Exception:
            metrics = {}
    return model, vect, metrics


def predict_email(subject: str, sender: str, content: str) -> Tuple[str, float, list, dict]:
    model, vect, metrics = load_artifacts()
    if model is None or vect is None:
        raise RuntimeError("Model not trained. Run train_model.py first.")

    text = (subject or "") + "\n" + (content or "")
    X = vect.transform([text])
    proba = model.predict_proba(X)[0]
    # Assuming classes [0=safe,1=phishing]
    phishing_conf = float(proba[1])
    label = "Phishing" if phishing_conf >= 0.5 else "Safe"

    feats = extract_features(subject, sender, content)

    reasons = []
    if feats["url_count"] > 0:
        reasons.append("Suspicious URL detected")
    if feats["suspicious_keywords"] > 0:
        reasons.append("Contains urgent/action keywords")
    if feats["sender_reputation"] < 0.4:
        reasons.append("Sender domain is suspicious")
    if feats["shortened_count"] > 0:
        reasons.append("Shortened URLs present")

    return label, phishing_conf, reasons, feats

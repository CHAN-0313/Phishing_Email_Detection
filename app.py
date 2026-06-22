import os
import io
import csv
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import bleach

from predictor import predict_email, load_artifacts
from train_model import train_and_save

BASE = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(BASE, "uploads")
SCANS_CSV = os.path.join(BASE, "scans.csv")
DATASET_DIR = os.path.join(BASE, "dataset")
ALLOWED_EXTENSIONS = {"csv", "txt"}

app = Flask(__name__, template_folder=os.path.join(BASE, "templates"), static_folder=os.path.join(BASE, "static"))
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_scan(subject, sender, result, confidence, features):
    exists = os.path.exists(SCANS_CSV)
    with open(SCANS_CSV, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["timestamp", "subject", "sender", "result", "confidence", "features"])
        writer.writerow([datetime.utcnow().isoformat(), subject, sender, result, f"{confidence:.4f}", json.dumps(features)])


@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    _, _, metrics = load_artifacts()
    return render_template("dashboard.html", metrics=metrics)


@app.route("/report")
def report_page():
    return render_template("report.html")


@app.route("/predict", methods=["POST"])
def api_predict():
    data = request.get_json() or {}
    subject = bleach.clean(data.get("subject", ""))
    sender = bleach.clean(data.get("sender", ""))
    content = bleach.clean(data.get("content", ""))
    try:
        label, conf, reasons, features = predict_email(subject, sender, content)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    save_scan(subject, sender, label, conf, features)

    return jsonify({
        "prediction": label,
        "confidence": f"{conf * 100:.1f}%",
        "confidence_raw": conf,
        "reasons": reasons,
        "features": features,
    })


@app.route("/upload_dataset", methods=["POST"])
def upload_dataset():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if f and allowed_file(f.filename):
        filename = secure_filename(f.filename)
        os.makedirs(DATASET_DIR, exist_ok=True)
        path = os.path.join(DATASET_DIR, filename)
        f.save(path)
        return jsonify({"message": "Dataset uploaded", "path": path})
    return jsonify({"error": "Invalid file type"}), 400


@app.route("/retrain", methods=["POST"])
def retrain():
    data = request.get_json() or {}
    dataset_path = data.get("dataset_path")
    if dataset_path:
        cleaned_path = os.path.normpath(os.path.join(BASE, dataset_path))
        if not cleaned_path.startswith(os.path.normpath(DATASET_DIR)):
            return jsonify({"error": "Invalid dataset path"}), 400
        if not os.path.exists(cleaned_path):
            return jsonify({"error": "Dataset file does not exist"}), 400
    try:
        metrics = train_and_save(dataset_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"message": "Retrained", "metrics": metrics})


@app.route("/metrics")
def metrics():
    _, _, metrics = load_artifacts()
    return jsonify(metrics or {})


@app.route("/scans")
def scans():
    rows = []
    if os.path.exists(SCANS_CSV):
        with open(SCANS_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    return jsonify(rows)


@app.route("/download_report", methods=["POST"])
def download_report():
    data = request.get_json() or {}
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    subject = data.get("subject", "")
    sender = data.get("sender", "")
    prediction = data.get("prediction", "")
    confidence = data.get("confidence", "")
    reasons = data.get("reasons", [])
    features = data.get("features", {})

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, height - 40, "Phishing Email Detection Report")
    c.setFont("Helvetica", 11)
    y = height - 80
    for label, value in [
        ("Subject", subject),
        ("Sender", sender),
        ("Prediction", prediction),
        ("Confidence", confidence),
        ("Timestamp", datetime.utcnow().isoformat()),
    ]:
        c.drawString(40, y, f"{label}: {value}")
        y -= 18

    y -= 8
    c.drawString(40, y, "Detection Reasons:")
    y -= 16
    for reason in reasons:
        c.drawString(60, y, f"- {reason}")
        y -= 14
        if y < 80:
            c.showPage()
            y = height - 40

    y -= 8
    c.drawString(40, y, "Extracted Features:")
    y -= 16
    for k, v in features.items():
        c.drawString(60, y, f"- {k}: {v}")
        y -= 14
        if y < 80:
            c.showPage()
            y = height - 40

    c.showPage()
    c.save()
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name="phishing_report.pdf", mimetype="application/pdf")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

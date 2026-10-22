from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from pathlib import Path
import uuid

from db import (
    create_patient,
    get_patients,
    get_patient,
    insert_reading,
    get_history
)
from predict import predict
from report import generate_report
from config import SERVER_HOST, SERVER_PORT

# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR.parent / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(
    __name__,
    template_folder=str(BASE_DIR.parent / "frontend" / "templates"),
    static_folder=str(BASE_DIR.parent / "frontend" / "static")
)
CORS(app)

# ============================================================
# ACTIVE DEVICE SESSION
# ============================================================

active_session = {
    "active": False,
    "patient_id": None
}

# ============================================================
# HOME / DASHBOARD
# ============================================================

@app.get("/")
def dashboard():
    return render_template("dashboard.html")

# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "HeartCare HTTP API"
    }), 200

# ============================================================
# GET ALL PATIENTS
# ============================================================

@app.get("/api/patients")
def patients():
    try:
        return jsonify(get_patients()), 200
    except Exception as e:
        app.logger.exception("PATIENT LIST ERROR")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ============================================================
# REGISTER PATIENT
# ============================================================

@app.post("/api/patients")
def add_patient():
    data = request.get_json(silent=True) or {}

    patient_id = str(data.get("patient_id", "")).strip()
    name = str(data.get("name", "")).strip()
    gender = str(data.get("gender", "")).strip()
    age = data.get("age")

    if not patient_id:
        return jsonify({
            "status": "error",
            "message": "Patient ID is required"
        }), 400

    if not name:
        return jsonify({
            "status": "error",
            "message": "Name is required"
        }), 400

    if not gender:
        return jsonify({
            "status": "error",
            "message": "Gender is required"
        }), 400

    if age is None or age == "":
        return jsonify({
            "status": "error",
            "message": "Age is required"
        }), 400

    try:
        age = int(age)
    except (TypeError, ValueError):
        return jsonify({
            "status": "error",
            "message": "Age must be a number"
        }), 400

    if age < 1 or age > 120:
        return jsonify({
            "status": "error",
            "message": "Age must be between 1 and 120"
        }), 400

    patient_data = {
        "patient_id": patient_id,
        "name": name,
        "age": age,
        "gender": gender
    }

    try:
        create_patient(patient_data)
        return jsonify({
            "status": "success",
            "message": "Patient registered successfully",
            "patient_id": patient_id
        }), 201
    except Exception as e:
        app.logger.exception("CREATE PATIENT ERROR")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ============================================================
# GET SINGLE PATIENT
# ============================================================

@app.get("/api/patients/<patient_id>")
def patient(patient_id):
    try:
        p = get_patient(patient_id)

        if not p:
            return jsonify({
                "status": "error",
                "message": "Patient not found"
            }), 404

        return jsonify(p), 200
    except Exception as e:
        app.logger.exception("GET PATIENT ERROR")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ============================================================
# START / STOP DEVICE SESSION
# ============================================================

@app.route("/api/device-session", methods=["GET", "POST"])
def device_session():
    global active_session

    # ESP32 reads the active session
    if request.method == "GET":
        return jsonify(active_session), 200

    data = request.get_json(silent=True) or {}

    # Stop monitoring
    if data.get("active") is False:
        active_session = {
            "active": False,
            "patient_id": None
        }

        print("Monitoring stopped")

        return jsonify({
            "status": "success",
            **active_session
        }), 200

    # Start monitoring
    patient_id = str(data.get("patient_id", "")).strip()

    if not patient_id:
        return jsonify({
            "status": "error",
            "message": "patient_id is required"
        }), 400

    try:
        patient_data = get_patient(patient_id)
    except Exception as e:
        app.logger.exception("SESSION PATIENT LOOKUP ERROR")
        return jsonify({
            "status": "error",
            "message": "Database error while looking up patient",
            "details": str(e)
        }), 500

    if not patient_data:
        return jsonify({
            "status": "error",
            "message": "Patient not found"
        }), 404

    active_session = {
        "active": True,
        "patient_id": patient_id
    }

    print("Active device session:", active_session)

    return jsonify({
        "status": "success",
        **active_session
    }), 200

# ============================================================
# RECEIVE SENSOR DATA, PREDICT AND SAVE TO DATABASE
# ============================================================

@app.post("/api/sensor-data")
def sensor_data():
    data = request.get_json(silent=True) or {}

    print("\n" + "=" * 60)
    print("SENSOR DATA REQUEST")
    print(data)
    print("=" * 60)

    patient_id = str(data.get("patient_id", "")).strip()

    if not patient_id:
        return jsonify({
            "status": "error",
            "message": "patient_id is required"
        }), 400

    # Get registered patient
    try:
        patient_data = get_patient(patient_id)
    except Exception as e:
        app.logger.exception("PATIENT DATABASE ERROR")
        return jsonify({
            "status": "error",
            "message": "Patient database error",
            "details": str(e)
        }), 500

    if not patient_data:
        return jsonify({
            "status": "error",
            "message": "Patient ID not registered"
        }), 404

    # Read sensor values
    try:
        age = int(data.get("age", patient_data["age"]))
        heart_rate = float(data.get("heart_rate", 0))
        spo2 = float(data.get("spo2", 0))
        ecg = float(data.get("ecg", 0))
    except (TypeError, ValueError) as e:
        return jsonify({
            "status": "error",
            "message": "Invalid sensor values",
            "details": str(e)
        }), 400

    ecg_voltage = data.get("ecg_voltage")
    ecg_status = data.get("ecg_status")

    print("Patient ID :", patient_id)
    print("Age        :", age)
    print("Heart Rate :", heart_rate)
    print("SpO2       :", spo2)
    print("ECG        :", ecg)
    print("ECG Voltage:", ecg_voltage)
    print("ECG Status :", ecg_status)

    # Run prediction
    try:
        result = predict(
            patient_data,
            heart_rate,
            spo2,
            ecg
        )
        print("Prediction result:", result)
    except Exception as e:
        app.logger.exception("PREDICTION ERROR")
        return jsonify({
            "status": "error",
            "message": "Prediction error",
            "details": str(e)
        }), 500

    # Save reading to MySQL
    try:
        reading_id = insert_reading(
            patient_id,
            age,
            heart_rate,
            spo2,
            ecg,
            result
        )
        print("DATABASE INSERT SUCCESS:", reading_id)
    except Exception as e:
        app.logger.exception("DATABASE INSERT ERROR")
        return jsonify({
            "status": "error",
            "message": "Database error",
            "details": str(e)
        }), 500

    # Build response
    response = {
        "status": "success",
        "reading_id": reading_id,
        "patient_id": patient_id,
        "age": age,
        "heart_rate": heart_rate,
        "spo2": spo2,
        "ecg": ecg,
        "ecg_voltage": ecg_voltage,
        "ecg_status": ecg_status
    }

    if isinstance(result, dict):
        response.update(result)

    return jsonify(response), 200

# ============================================================
# PATIENT HISTORY
# ============================================================

@app.get("/api/history/<patient_id>")
def history(patient_id):
    try:
        patient_data = get_patient(patient_id)

        if not patient_data:
            return jsonify({
                "status": "error",
                "message": "Patient not found"
            }), 404

        rows = get_history(patient_id)
        return jsonify(rows), 200
    except Exception as e:
        app.logger.exception("HISTORY ERROR")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ============================================================
# GENERATE AND DOWNLOAD PDF REPORT
# ============================================================

@app.get("/api/report/<patient_id>")
def report(patient_id):
    try:
        patient_data = get_patient(patient_id)

        if not patient_data:
            return jsonify({
                "status": "error",
                "message": "Patient not found"
            }), 404

        history_rows = get_history(patient_id)

        if not history_rows:
            return jsonify({
                "status": "error",
                "message": "No sensor history available"
            }), 404

        filename = (
            f"HeartCare_{patient_id}_"
            f"{uuid.uuid4().hex[:8]}.pdf"
        )
        output_path = REPORT_DIR / filename

        generate_report(
            patient_data,
            history_rows,
            output_path
        )

        if not output_path.exists():
            return jsonify({
                "status": "error",
                "message": "PDF file was not created"
            }), 500

        return send_file(
            str(output_path),
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf"
        )
    except Exception as e:
        app.logger.exception("PDF REPORT ERROR")
        return jsonify({
            "status": "error",
            "message": "PDF generation failed",
            "details": str(e)
        }), 500

# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("HEARTCARE IoT SERVER")
    print("Server :", SERVER_HOST)
    print("Port   :", SERVER_PORT)
    print("Reports:", REPORT_DIR)
    print("=" * 60)

    app.run(
        host=SERVER_HOST,
        port=SERVER_PORT,
        debug=True
    )
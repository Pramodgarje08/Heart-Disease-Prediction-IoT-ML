from pathlib import Path
import joblib
import pandas as pd

MODEL = Path(__file__).resolve().parents[1] / "models" / "heart_india_model.joblib"


def insufficient_data():
    return {
        "prediction": "Insufficient Sensor Data",
        "risk_level": "Data Insufficient",
        "score": 0,
        "confidence": 0.0,
        "model": "sensor_validation"
    }


def sensor_data_complete(hr, spo2, ecg):
    hr_valid = hr > 0
    spo2_valid = 0 < spo2 <= 100
    ecg_valid = ecg > 0

    return hr_valid and spo2_valid and ecg_valid


def fallback(age, hr, spo2, ecg):

    if not sensor_data_complete(hr, spo2, ecg):
        return insufficient_data()

    score = 0

    if age >= 55:
        score += 1

    if hr < 50 or hr > 120:
        score += 2
    elif hr < 60 or hr > 100:
        score += 1

    if spo2 < 92:
        score += 2
    elif spo2 < 95:
        score += 1

    if score >= 4:
        risk = "High"
        prediction = "Higher Risk Pattern"

    elif score >= 2:
        risk = "Medium"
        prediction = "Needs Review"

    else:
        risk = "Low"
        prediction = "Lower Risk Pattern"

    return {
        "prediction": prediction,
        "risk_level": risk,
        "score": score,
        "confidence": 0.70,
        "model": "fallback"
    }


def gender_value(gender):

    if isinstance(gender, (int, float)):
        return gender

    gender = str(gender).lower()

    if gender == "male":
        return 1

    if gender == "female":
        return 0

    return 0


def predict(patient, hr, spo2, ecg):

    age = int(patient.get("age", 0))

    hr = float(hr or 0)
    spo2 = float(spo2 or 0)
    ecg = float(ecg or 0)

    # --------------------------------------------------------
    # SENSOR VALIDATION
    # --------------------------------------------------------

    if not sensor_data_complete(hr, spo2, ecg):
        return insufficient_data()

    # --------------------------------------------------------
    # MODEL CHECK
    # --------------------------------------------------------

    if not MODEL.exists():
        return fallback(
            age,
            hr,
            spo2,
            ecg
        )

    try:

        artifact = joblib.load(MODEL)

        model = artifact["model"]
        features = artifact["features"]

        values = {
            "age": age,

            "gender": gender_value(
                patient.get("gender", 0)
            ),

            "chestpain":
                patient.get("chest_pain", 0),

            "restingbp":
                patient.get("resting_bp", 120),

            "cholesterol":
                patient.get("cholesterol", 200),

            "fastingbs":
                patient.get("fasting_blood_sugar", 0),

            "restingecg":
                patient.get("resting_ecg", 0),

            "maxheartrate":
                hr,

            "exerciseangina":
                patient.get("exercise_angina", 0),

            "oldpeak":
                patient.get("oldpeak", 0),

            "slope":
                patient.get("slope", 1),

            "majorvessels":
                patient.get("major_vessels", 0)
        }

        row = {
            feature: values.get(feature, 0)
            for feature in features
        }

        X = pd.DataFrame(
            [row],
            columns=features
        )

        # ----------------------------------------------------
        # ML PREDICTION
        # ----------------------------------------------------

        prediction = int(
            model.predict(X)[0]
        )

        if hasattr(model, "predict_proba"):

            probability = model.predict_proba(X)[0]

            confidence = float(
                max(probability)
            )

        else:

            confidence = 0.70

        if prediction == 1:

            result = "Heart Disease Risk Detected"
            risk = "High"

        else:

            result = "No Heart Disease Pattern"
            risk = "Low"

        # ----------------------------------------------------
        # SpO2 SAFETY ADJUSTMENT
        # ----------------------------------------------------

        if spo2 < 90:

            risk = "High"
            result = "Low SpO2 - Needs Review"

        elif spo2 < 95 and risk == "Low":

            risk = "Medium"
            result = "Needs Review"

        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        return {
            "prediction": result,
            "risk_level": risk,
            "score": prediction,
            "confidence": confidence,
            "model": artifact.get(
                "model_name",
                "heart_india_model"
            )
        }

    except Exception as e:

        print(
            "ML prediction error:",
            e
        )

        return fallback(
            age,
            hr,
            spo2,
            ecg
        )
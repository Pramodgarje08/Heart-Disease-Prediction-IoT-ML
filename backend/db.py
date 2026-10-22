import mysql.connector

from config import (
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
    DB_PORT
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )


# =========================================================
# CREATE PATIENT
# =========================================================

def create_patient(data):

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO patients
            (patient_id, name, age, gender)
            VALUES (%s, %s, %s, %s)
        """, (
            data["patient_id"],
            data["name"],
            int(data["age"]),
            data["gender"]
        ))

        conn.commit()

        print("====================================")
        print("PATIENT CREATED")
        print("Patient ID:", data["patient_id"])
        print("Name:", data["name"])
        print("Age:", data["age"])
        print("Gender:", data["gender"])
        print("====================================")

    except Exception as e:

        if conn:
            conn.rollback()

        print("CREATE PATIENT ERROR:", str(e))

        raise

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()


# =========================================================
# GET ALL PATIENTS
# =========================================================

def get_patients():

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT
                patient_id,
                name,
                age,
                gender
            FROM patients
            ORDER BY id DESC
        """)

        rows = cur.fetchall()

        return rows

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()


# =========================================================
# GET SINGLE PATIENT
# =========================================================

def get_patient(patient_id):

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT *
            FROM patients
            WHERE patient_id = %s
        """, (patient_id,))

        row = cur.fetchone()

        print("GET PATIENT:", patient_id)
        print("PATIENT RESULT:", row)

        return row

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()


# =========================================================
# INSERT SENSOR READING + PREDICTION
# =========================================================

def insert_reading(
    patient_id,
    age,
    heart_rate,
    spo2,
    ecg,
    prediction
):

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor()

        print("\n====================================")
        print("INSERTING SENSOR DATA")
        print("Patient ID :", patient_id)
        print("Age        :", age)
        print("Heart Rate :", heart_rate)
        print("SpO2       :", spo2)
        print("ECG        :", ecg)
        print("Prediction :", prediction)
        print("====================================")

        # -----------------------------------------
        # INSERT SENSOR READING
        # -----------------------------------------

        cur.execute("""
            INSERT INTO sensor_readings
            (
                patient_id,
                age_at_test,
                heart_rate,
                spo2,
                ecg
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            patient_id,
            age,
            heart_rate,
            spo2,
            ecg
        ))

        reading_id = cur.lastrowid

        print("Sensor Reading ID:", reading_id)

        # -----------------------------------------
        # INSERT PREDICTION
        # -----------------------------------------

        cur.execute("""
            INSERT INTO predictions
            (
                patient_id,
                reading_id,
                prediction,
                risk_level,
                score,
                confidence,
                model_name
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            patient_id,
            reading_id,
            prediction["prediction"],
            prediction["risk_level"],
            prediction["score"],
            prediction["confidence"],
            prediction.get("model", "unknown")
        ))

        # -----------------------------------------
        # COMMIT
        # -----------------------------------------

        conn.commit()

        print("DATABASE COMMIT SUCCESS")
        print("Reading ID:", reading_id)
        print("====================================\n")

        return reading_id

    except Exception as e:

        if conn:
            conn.rollback()

        print("\n====================================")
        print("DATABASE ERROR")
        print(str(e))
        print("====================================\n")

        raise

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()


# =========================================================
# GET PATIENT HISTORY
# =========================================================

def get_history(patient_id, limit=200):

    conn = None
    cur = None

    try:

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT
                s.id,
                s.timestamp,
                s.age_at_test,
                s.heart_rate,
                s.spo2,
                s.ecg,
                p.prediction,
                p.risk_level,
                p.score,
                p.confidence,
                p.model_name
            FROM sensor_readings s

            LEFT JOIN predictions p
                ON p.reading_id = s.id

            WHERE s.patient_id = %s

            ORDER BY s.id DESC

            LIMIT %s
        """, (
            patient_id,
            limit
        ))

        rows = cur.fetchall()

        return rows

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()
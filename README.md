# HEARTCARE FINAL MEGA PROJECT
## ESP32 + MAX30102 + AD8232 + HTTP + Flask + MySQL

This final project contains:
- Patient registration
- Patient ID and age entered by the user through the web dashboard
- MAX30102: Heart Rate + SpO2
- AD8232: ECG signal
- ESP32 Wi-Fi
- HTTP REST communication (NO MQTT)
- Flask backend
- MySQL patient/history database
- Live monitoring dashboard
- Heart-risk demonstration prediction
- Patient history
- PDF report generation

NETWORK
Wi-Fi SSID: PRAMOD
Wi-Fi password: 11111111
PC IP: 10.15.72.84
Flask port: 5000

SENSORS
MAX30102:
VIN -> 3.3V
GND -> GND
SDA -> GPIO21
SCL -> GPIO22

AD8232:
OUTPUT -> GPIO34
LO+ -> GPIO25
LO- -> GPIO26
3.3V -> 3.3V
GND -> GND

ARDUINO LIBRARY
Install:
SparkFun MAX3010x Pulse and Proximity Sensor Library

IMPORTANT
The prediction included in this package is a transparent demonstration risk score,
not a validated medical diagnostic model. Do not use it for clinical decisions.
For a final academic project, replace backend/predict.py with your validated model.

START
1. Run database/schema.sql in MySQL Workbench.
2. Edit backend/config.py and set your MySQL password.
3. Create venv:
   python -m venv venv
4. Activate:
   venv\Scripts\activate
5. Install:
   pip install -r backend/requirements.txt
6. Test DB:
   python backend/test_db.py
7. Start Flask:
   python backend/app.py
8. Open:
   http://10.15.72.84:5000
9. Register a patient from the dashboard.
10. Upload the ESP32 sketch.
11. Enter the Patient ID in the ESP32 Serial Monitor when requested.
12. Put finger on MAX30102 and attach AD8232 electrodes.
13. Open Live Monitoring.
14. Generate PDF report from Patient History.

PATIENT DATA
Do not put the patient's name/age into Python code.
Enter it in Dashboard -> Register Patient.
The ESP32 asks for Patient ID and Age in Serial Monitor, so the same patient
can be selected for a monitoring session.

DATA FLOW
Patient -> Registration -> MySQL
MAX30102 -> HR + SpO2
AD8232 -> ECG
ESP32 -> HTTP -> Flask -> MySQL
                              -> Prediction
                              -> Dashboard
                              -> PDF report

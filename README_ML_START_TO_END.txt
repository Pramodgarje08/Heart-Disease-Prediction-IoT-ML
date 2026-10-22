HEARTCARE FINAL MEGA PROJECT - ML INDIA

CONFIG:
Wi-Fi: PRAMOD
Wi-Fi password: 11111111
PC IP: 10.15.72.84
Flask: 5000
MySQL user: root
MySQL password: root
MQTT: NOT USED

SENSORS:
MAX30102 -> HR. SpO2 is not calculated yet; 0 means not measured.
AD8232 -> ECG analog signal.

ML DATASET:
Indian Cardiovascular_Disease_Dataset (Doppala & Bhattacharyya), Mendeley Data V1.
https://data.mendeley.com/datasets/dzz48mvjht/1

RUN:
1. MySQL Workbench -> run database/schema.sql
2. python -m venv venv
3. venv\Scripts\activate
4. pip install -r backend\requirements.txt
5. python backend\test_db.py
6. python ml\download_dataset.py
7. python ml\train_model.py
8. python backend\app.py
9. Browser: http://10.15.72.84:5000
10. Register patient in dashboard.
11. Upload esp32\heart_monitor\heart_monitor.ino
12. Serial Monitor 115200: enter Patient ID and Age.
13. Put finger on MAX30102 and connect AD8232 electrodes.
14. Check HTTP 200, Live Monitoring, History and PDF Report.

If HTTP -1 connection refused: Flask must be running, PC must have 10.15.72.84,
and TCP 5000 must be allowed in Windows Firewall.

The ML result is an academic risk-screening prototype, not a medical diagnosis.

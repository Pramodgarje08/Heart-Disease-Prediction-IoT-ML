CREATE DATABASE IF NOT EXISTS heartcare_iot;
USE heartcare_iot;

CREATE TABLE IF NOT EXISTS patients (
 id INT AUTO_INCREMENT PRIMARY KEY,
 patient_id VARCHAR(30) UNIQUE NOT NULL,
 name VARCHAR(150) NOT NULL,
 age INT NOT NULL,
 gender VARCHAR(20) NOT NULL,
 phone VARCHAR(30), email VARCHAR(150), address VARCHAR(255), blood_group VARCHAR(10),
 height_cm FLOAT, weight_kg FLOAT, emergency_contact VARCHAR(100),
 resting_bp FLOAT DEFAULT 120, cholesterol FLOAT DEFAULT 200,
 fasting_blood_sugar INT DEFAULT 0, chest_pain INT DEFAULT 0, resting_ecg INT DEFAULT 0,
 exercise_angina INT DEFAULT 0, max_heart_rate FLOAT DEFAULT 80, oldpeak FLOAT DEFAULT 0,
 slope INT DEFAULT 1, major_vessels INT DEFAULT 0,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sensor_readings (
 id BIGINT AUTO_INCREMENT PRIMARY KEY,
 patient_id VARCHAR(30) NOT NULL,
 age_at_test INT NOT NULL,
 heart_rate FLOAT NOT NULL,
 spo2 FLOAT DEFAULT 0,
 ecg FLOAT NOT NULL,
 timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE ON UPDATE CASCADE,
 INDEX idx_patient_time(patient_id,timestamp)
);

CREATE TABLE IF NOT EXISTS predictions (
 id BIGINT AUTO_INCREMENT PRIMARY KEY,
 patient_id VARCHAR(30) NOT NULL,
 reading_id BIGINT,
 prediction VARCHAR(100), risk_level VARCHAR(50), score INT, confidence FLOAT,
 model_name VARCHAR(100), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE ON UPDATE CASCADE,
 FOREIGN KEY(reading_id) REFERENCES sensor_readings(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS medical_history (
 id INT AUTO_INCREMENT PRIMARY KEY,
 patient_id VARCHAR(30) NOT NULL,
 condition_name VARCHAR(200), medication VARCHAR(200), notes TEXT, date DATE,
 FOREIGN KEY(patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE ON UPDATE CASCADE
);

#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <ArduinoJson.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"

// =====================================================
// 1. WI-FI AND SERVER CONFIGURATION
// =====================================================

const char* WIFI_SSID = "PG";
const char* WIFI_PASSWORD = "86008600";

const char* SERVER_IP = "10.63.129.84";

String SESSION_URL =
    String("http://") + SERVER_IP + ":5000/api/device-session";

String SENSOR_URL =
    String("http://") + SERVER_IP + ":5000/api/sensor-data";

// =====================================================
// 2. SENSOR PINS
// =====================================================

#define ECG_PIN 34
#define LO1_PIN 25
#define LO2_PIN 26

// =====================================================
// 3. MAX30102 CONFIGURATION
// =====================================================

constexpr int SENSOR_BUFFER_SIZE = 100;
constexpr int FILTER_SIZE = 5;

constexpr uint32_t MIN_AVERAGE_IR = 50000;

MAX30105 pulseSensor;

uint32_t irBuffer[SENSOR_BUFFER_SIZE];
uint32_t redBuffer[SENSOR_BUFFER_SIZE];

int32_t rawSpO2 = 0;
int32_t rawHeartRate = 0;

int8_t validSpO2 = 0;
int8_t validHeartRate = 0;

int heartRate = 0;
int spo2 = 0;

uint32_t averageIR = 0;

int hrHistory[FILTER_SIZE] = {};
int spo2History[FILTER_SIZE] = {};

int historyIndex = 0;
int historyCount = 0;

// =====================================================
// 4. MONITORING SESSION
// =====================================================

String patientId = "";

unsigned long lastSessionCheck = 0;
unsigned long lastSensorSend = 0;

constexpr unsigned long SESSION_INTERVAL_MS = 2000;
constexpr unsigned long SEND_INTERVAL_MS = 1000;

// =====================================================
// 5. CONNECT TO WI-FI
// =====================================================

bool connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) {
    return true;
  }

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Connecting to Wi-Fi...");

  unsigned long started = millis();

  while (WiFi.status() != WL_CONNECTED &&
         millis() - started < 15000) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWi-Fi connected");
    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.localIP());

    return true;
  }

  Serial.println("\nWi-Fi connection failed");
  return false;
}

// =====================================================
// 6. MEDIAN FILTER
// =====================================================

int medianValue(const int values[], int count) {
  if (count <= 0) {
    return 0;
  }

  int sorted[FILTER_SIZE];

  for (int i = 0; i < count; i++) {
    sorted[i] = values[i];
  }

  for (int i = 0; i < count - 1; i++) {
    for (int j = i + 1; j < count; j++) {
      if (sorted[i] > sorted[j]) {
        int temp = sorted[i];
        sorted[i] = sorted[j];
        sorted[j] = temp;
      }
    }
  }

  return sorted[count / 2];
}

// =====================================================
// 7. GET ACTIVE PATIENT FROM FLASK
// =====================================================

bool getDeviceSession() {
  if (WiFi.status() != WL_CONNECTED) {
    return false;
  }

  HTTPClient http;
  http.setTimeout(3000);

  if (!http.begin(SESSION_URL)) {
    Serial.println("Session HTTP initialization failed");
    return false;
  }

  int code = http.GET();

  String response = "";

  if (code == HTTP_CODE_OK) {
    response = http.getString();
  }

  http.end();

  if (code != HTTP_CODE_OK) {
    Serial.printf("Session HTTP error: %d\n", code);
    return false;
  }

  JsonDocument doc;

  DeserializationError error =
      deserializeJson(doc, response);

  if (error) {
    Serial.println("Session JSON parsing failed");
    return false;
  }

  bool active = doc["active"] | false;

  String newPatientId =
      doc["patient_id"] | "";

  newPatientId.trim();

  if (active && newPatientId.length() > 0) {
    if (patientId != newPatientId) {
      patientId = newPatientId;

      historyIndex = 0;
      historyCount = 0;

      heartRate = 0;
      spo2 = 0;

      Serial.println("==============================");
      Serial.println("Monitoring session started");
      Serial.print("Patient ID: ");
      Serial.println(patientId);
      Serial.println("==============================");
    }

    return true;
  }

  if (patientId.length() > 0) {
    Serial.println("Monitoring session stopped");
  }

  patientId = "";

  return false;
}

// =====================================================
// 8. READ MAX30102 HEART RATE AND SPO2
// =====================================================

bool readPulseSensor() {
  uint64_t irSum = 0;

  for (int i = 0; i < SENSOR_BUFFER_SIZE; i++) {
    unsigned long started = millis();

    while (!pulseSensor.available()) {
      pulseSensor.check();

      if (millis() - started > 2000) {
        heartRate = 0;
        spo2 = 0;

        Serial.println("MAX30102 sample timeout");
        return false;
      }

      delay(1);
    }

    redBuffer[i] = pulseSensor.getRed();
    irBuffer[i] = pulseSensor.getIR();

    irSum += irBuffer[i];

    pulseSensor.nextSample();
  }

  averageIR = irSum / SENSOR_BUFFER_SIZE;

  // Check if finger signal is strong enough
  if (averageIR < MIN_AVERAGE_IR) {
    heartRate = 0;
    spo2 = 0;

    Serial.printf(
        "Weak signal, average IR: %lu\n",
        (unsigned long)averageIR
    );

    return false;
  }

  // Calculate HR and SpO2
  maxim_heart_rate_and_oxygen_saturation(
      irBuffer,
      SENSOR_BUFFER_SIZE,
      redBuffer,
      &rawSpO2,
      &validSpO2,
      &rawHeartRate,
      &validHeartRate
  );

  bool hrOK =
      validHeartRate &&
      rawHeartRate >= 30 &&
      rawHeartRate <= 200;

  bool spo2OK =
      validSpO2 &&
      rawSpO2 >= 70 &&
      rawSpO2 <= 100;

  if (!hrOK || !spo2OK) {
    heartRate = 0;
    spo2 = 0;

    Serial.println("Invalid MAX30102 reading");
    return false;
  }

  // Save readings for median filtering
  hrHistory[historyIndex] = rawHeartRate;
  spo2History[historyIndex] = rawSpO2;

  historyIndex = (historyIndex + 1) % FILTER_SIZE;

  if (historyCount < FILTER_SIZE) {
    historyCount++;
  }

  heartRate = medianValue(hrHistory, historyCount);
  spo2 = medianValue(spo2History, historyCount);

  return true;
}

// =====================================================
// 9. SEND SENSOR DATA TO FLASK
// =====================================================

void sendSensorData(
    int ecg,
    float voltage,
    const String& status
) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi disconnected; data not sent");
    return;
  }

  if (patientId.length() == 0) {
    Serial.println("No active patient; data not sent");
    return;
  }

  HTTPClient http;
  http.setTimeout(5000);

  if (!http.begin(SENSOR_URL)) {
    Serial.println("Sensor HTTP initialization failed");
    return;
  }

  http.addHeader(
      "Content-Type",
      "application/json"
  );

  JsonDocument doc;

  doc["patient_id"] = patientId;
  doc["heart_rate"] = heartRate;
  doc["spo2"] = spo2;
  doc["ecg"] = ecg;
  doc["ecg_voltage"] = voltage;
  doc["ecg_status"] = status;

  String payload;

  serializeJson(doc, payload);

  Serial.println("Sending sensor data:");
  Serial.println(payload);

  int code = http.POST(payload);

  Serial.printf("Sensor HTTP code: %d\n", code);

  if (code > 0) {
    String response = http.getString();

    Serial.println("Server response:");
    Serial.println(response);
  } else {
    Serial.println(http.errorToString(code));
  }

  http.end();
}

// =====================================================
// 10. SETUP
// =====================================================

void setup() {
  Serial.begin(115200);

  pinMode(ECG_PIN, INPUT);
  pinMode(LO1_PIN, INPUT);
  pinMode(LO2_PIN, INPUT);

  analogReadResolution(12);
  analogSetPinAttenuation(ECG_PIN, ADC_11db);

  Wire.begin(21, 22);

  if (!connectWiFi()) {
    Serial.println("Restart ESP32 if Wi-Fi cannot connect");
  }

  Serial.println("Initializing MAX30102...");

  if (!pulseSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("MAX30102 not found. Check wiring.");

    while (true) {
      delay(1000);
    }
  }

  pulseSensor.setup(
      0x24,  // LED amplitude
      4,     // Sample average
      2,     // Red + IR LEDs
      100,   // Sample rate
      411,   // Pulse width
      4096   // ADC range
  );

  pulseSensor.setPulseAmplitudeRed(0x24);
  pulseSensor.setPulseAmplitudeIR(0x24);
  pulseSensor.setPulseAmplitudeGreen(0);

  Serial.println("==============================");
  Serial.println("HeartCare ESP32 ready");
  Serial.println("Open dashboard and start monitoring");
  Serial.println("==============================");
}

// =====================================================
// 11. MAIN LOOP
// =====================================================

void loop() {
  if (!connectWiFi()) {
    delay(500);
    return;
  }

  // Check the active session
  if (millis() - lastSessionCheck >=
      SESSION_INTERVAL_MS) {

    lastSessionCheck = millis();

    getDeviceSession();
  }

  // Read ECG lead-off status
  bool leadOff =
      digitalRead(LO1_PIN) == HIGH ||
      digitalRead(LO2_PIN) == HIGH;

  // Average 5 ECG samples
  long ecgSum = 0;

  for (int i = 0; i < 5; i++) {
    ecgSum += analogRead(ECG_PIN);
    delayMicroseconds(500);
  }

  int ecgValue = ecgSum / 5;

  float voltage =
      ecgValue * 3.3f / 4095.0f;

  String ecgStatus =
      leadOff ? "LEAD_OFF" :
      (ecgValue >= 4080 || ecgValue <= 15)
          ? "SATURATED"
          : "SIGNAL_OK";

  // Read MAX30102
  readPulseSensor();

  Serial.printf(
      "ECG:%d | V:%.3f | %s | HR:%d | SpO2:%d | IR:%lu | Patient:%s\n",
      ecgValue,
      voltage,
      ecgStatus.c_str(),
      heartRate,
      spo2,
      (unsigned long)averageIR,
      patientId.c_str()
  );

  // Send data only when a patient session is active
  if (millis() - lastSensorSend >=
      SEND_INTERVAL_MS) {

    lastSensorSend = millis();

    if (patientId.length() > 0) {
      sendSensorData(
          ecgValue,
          voltage,
          ecgStatus
      );
    }
  }

  delay(10);
}
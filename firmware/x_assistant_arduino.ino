/*
 * X Assistant - Production Arduino Firmware (Phase 4)
 * 
 * Target Boards: Arduino Uno / Nano / Mega / ESP8266 / ESP32
 * Communication: USB Serial @ 9600 Baud Rate
 * Protocol: Two-way JSON command parsing and sensor telemetry broadcasting
 */

#include <Arduino.h>

// Sensor Pin Definitions
const int PIN_RELAY_LIGHT = 7;
const int PIN_RELAY_FAN   = 8;
const int PIN_SERVO       = 9;
const int PIN_BUZZER      = 10;
const int PIN_PIR_MOTION  = 2;
const int PIN_GAS_SENSOR  = A0;
const int PIN_LDR_LIGHT   = A1;
const int PIN_RAIN_SENSOR = A2;
const int PIN_LED_BUILDIN = 13;

unsigned long lastSensorReport = 0;
const unsigned long REPORT_INTERVAL = 3000; // Broadcast sensor telemetry every 3 seconds

void setup() {
  Serial.begin(9600);
  
  pinMode(PIN_RELAY_LIGHT, OUTPUT);
  pinMode(PIN_RELAY_FAN, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED_BUILDIN, OUTPUT);
  pinMode(PIN_PIR_MOTION, INPUT);

  // Initial State: OFF (Active Low Relays default HIGH)
  digitalWrite(PIN_RELAY_LIGHT, HIGH);
  digitalWrite(PIN_RELAY_FAN, HIGH);
  digitalWrite(PIN_BUZZER, LOW);
  digitalWrite(PIN_LED_BUILDIN, LOW);

  // Ready Handshake
  Serial.println("{\"status\":\"READY\",\"board\":\"Arduino_Uno\",\"version\":\"4.0\"}");
}

void loop() {
  // 1. Listen for incoming Serial commands from Python X Assistant
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    if (input.length() > 0) {
      processCommand(input);
    }
  }

  // 2. Periodic Sensor Telemetry Broadcast
  if (millis() - lastSensorReport >= REPORT_INTERVAL) {
    lastSensorReport = millis();
    broadcastSensorData();
  }
}

void processCommand(String cmdJson) {
  cmdJson.toLowerCase();

  // Simple, robust JSON string matching (no external heavy library required)
  if (cmdJson.indexOf("ping") >= 0) {
    Serial.println("{\"response\":\"PONG\",\"status\":\"ONLINE\"}");
  }
  else if (cmdJson.indexOf("relay_light_on") >= 0 || (cmdJson.indexOf("relay_on") >= 0 && cmdJson.indexOf("7") >= 0)) {
    digitalWrite(PIN_RELAY_LIGHT, LOW); // ON
    Serial.println("{\"ack\":\"RELAY_LIGHT_ON\",\"pin\":7}");
  }
  else if (cmdJson.indexOf("relay_light_off") >= 0 || (cmdJson.indexOf("relay_off") >= 0 && cmdJson.indexOf("7") >= 0)) {
    digitalWrite(PIN_RELAY_LIGHT, HIGH); // OFF
    Serial.println("{\"ack\":\"RELAY_LIGHT_OFF\",\"pin\":7}");
  }
  else if (cmdJson.indexOf("relay_fan_on") >= 0 || (cmdJson.indexOf("relay_on") >= 0 && cmdJson.indexOf("8") >= 0)) {
    digitalWrite(PIN_RELAY_FAN, LOW); // ON
    Serial.println("{\"ack\":\"RELAY_FAN_ON\",\"pin\":8}");
  }
  else if (cmdJson.indexOf("relay_fan_off") >= 0 || (cmdJson.indexOf("relay_off") >= 0 && cmdJson.indexOf("8") >= 0)) {
    digitalWrite(PIN_RELAY_FAN, HIGH); // OFF
    Serial.println("{\"ack\":\"RELAY_FAN_OFF\",\"pin\":8}");
  }
  else if (cmdJson.indexOf("buzzer_on") >= 0) {
    digitalWrite(PIN_BUZZER, HIGH);
    Serial.println("{\"ack\":\"BUZZER_ON\",\"pin\":10}");
  }
  else if (cmdJson.indexOf("buzzer_off") >= 0) {
    digitalWrite(PIN_BUZZER, LOW);
    Serial.println("{\"ack\":\"BUZZER_OFF\",\"pin\":10}");
  }
  else if (cmdJson.indexOf("blink") >= 0) {
    for (int i = 0; i < 5; i++) {
      digitalWrite(PIN_LED_BUILDIN, HIGH);
      delay(200);
      digitalWrite(PIN_LED_BUILDIN, LOW);
      delay(200);
    }
    Serial.println("{\"ack\":\"BLINK_COMPLETE\",\"count\":5}");
  }
  else if (cmdJson.indexOf("all_relays_on") >= 0) {
    digitalWrite(PIN_RELAY_LIGHT, LOW);
    digitalWrite(PIN_RELAY_FAN, LOW);
    Serial.println("{\"ack\":\"ALL_RELAYS_ON\"}");
  }
  else if (cmdJson.indexOf("all_relays_off") >= 0) {
    digitalWrite(PIN_RELAY_LIGHT, HIGH);
    digitalWrite(PIN_RELAY_FAN, HIGH);
    Serial.println("{\"ack\":\"ALL_RELAYS_OFF\"}");
  }
}

void broadcastSensorData() {
  int motionVal = digitalRead(PIN_PIR_MOTION);
  int gasVal = analogRead(PIN_GAS_SENSOR);
  int ldrVal = analogRead(PIN_LDR_LIGHT);
  int rainVal = analogRead(PIN_RAIN_SENSOR);

  // Simulated Temp & Humidity if DHT sensor library not included
  float tempC = 28.5 + (random(-10, 10) / 10.0);
  float humidity = 65.0 + (random(-20, 20) / 10.0);

  String jsonStr = "{\"telemetry\":true";
  jsonStr += ",\"temp\":" + String(tempC, 1);
  jsonStr += ",\"humidity\":" + String(humidity, 1);
  jsonStr += ",\"motion\":" + String(motionVal);
  jsonStr += ",\"gas\":" + String(gasVal);
  jsonStr += ",\"ldr\":" + String(ldrVal);
  jsonStr += ",\"rain\":" + String(rainVal);
  jsonStr += "}";

  Serial.println(jsonStr);
}

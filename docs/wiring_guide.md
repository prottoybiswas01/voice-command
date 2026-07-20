# Hardware Pinout & Wiring Guide - X Assistant (Phase 4) ⚡

This document details the hardware wiring schematics and pin mappings for connecting Arduino boards (Uno, Nano, Mega) with X Assistant.

---

## 📌 Standard Pin Mapping Table

| Component | Component Type | Arduino Pin | Description / Function |
|---|---|---|---|
| **Relay 1** | Output Actuator | **Digital Pin 7** | Room Light Control (Active LOW Relay) |
| **Relay 2** | Output Actuator | **Digital Pin 8** | Room Fan Control (Active LOW Relay) |
| **Servo Motor** | Output Actuator | **Digital Pin 9** | Door Lock Mechanism (0° - 180° rotation) |
| **Buzzer** | Output Actuator | **Digital Pin 10** | Security Alarm & Emergency Alert Buzzer |
| **Status LED** | Output Actuator | **Digital Pin 13** | Built-in LED / Voice Command Status Indicator |
| **PIR Motion** | Input Sensor | **Digital Pin 2** | Motion & Intruder Detection Sensor |
| **Gas Sensor (MQ2)**| Input Sensor | **Analog Pin A0** | Gas Leak & Smoke Detector Sensor |
| **LDR Light Sensor**| Input Sensor | **Analog Pin A1** | Ambient Room Light Sensor |
| **Rain Sensor** | Input Sensor | **Analog Pin A2** | Rain Detection Sensor Module |

---

## 🔌 Circuit Connection Schematics

### 1. 2-Channel Relay Module Wiring
- **VCC** ➔ Arduino **5V**
- **GND** ➔ Arduino **GND**
- **IN1 (Light)** ➔ Arduino **Digital Pin 7**
- **IN2 (Fan)** ➔ Arduino **Digital Pin 8**

### 2. PIR Motion Sensor Wiring
- **VCC** ➔ Arduino **5V**
- **GND** ➔ Arduino **GND**
- **OUT / DATA** ➔ Arduino **Digital Pin 2**

### 3. MQ2 Gas / Smoke Sensor Wiring
- **VCC** ➔ Arduino **5V**
- **GND** ➔ Arduino **GND**
- **A0 (Analog Out)** ➔ Arduino **Analog Pin A0**

### 4. Servo Motor Wiring
- **VCC (Red)** ➔ External 5V Power Supply / Arduino 5V
- **GND (Black/Brown)** ➔ Common Ground (Arduino GND)
- **PWM Signal (Yellow/Orange)** ➔ Arduino **Digital Pin 9**

---

## ⚡ Baud Rate & Serial Communication
- **Baud Rate**: `9600`
- **Protocol**: JSON Line Encoded Packets
  - Command: `{"cmd":"RELAY_LIGHT_ON"}`
  - Telemetry: `{"telemetry":true, "temp":28.5, "humidity":65, "motion":1, "gas":120}`

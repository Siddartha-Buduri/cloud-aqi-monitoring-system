# Cloud-Based AQI Monitoring and Visualization System

An academic IoT project for collecting air-quality sensor measurements at an edge device, processing the readings, and transmitting AQI data to AWS IoT using MQTT over TLS.

The project combines sensor data acquisition, edge-side processing, MQTT communication, cloud connectivity, and AQI visualization.

---

## 📌 Project Overview

The system collects environmental measurements from multiple air-quality sensors through a serial interface connected to an edge device.

A Python-based edge gateway:

- Reads sensor data through a serial interface.
- Extracts sensor measurements and AQI values.
- Builds structured JSON payloads.
- Maintains the latest sensor readings locally.
- Publishes the data to AWS IoT using MQTT.
- Uses TLS certificates for MQTT communication.
- Displays the latest readings through a local terminal dashboard.

The transmitted data can be monitored through the AWS IoT MQTT test client and visualized through the project's AQI dashboard.

---

## 🏗️ System Architecture

```text
┌───────────────────────────────┐
│       Air Quality Sensors     │
│                               │
│ PM2.5 | MQ-135 | MQ-7         │
│ MQ-136 | MQ-131               │
└───────────────┬───────────────┘
                │
                │ Serial
                ▼
┌───────────────────────────────┐
│       Edge Gateway            │
│                               │
│ Python                        │
│ Serial Data Acquisition       │
│ Data Parsing                  │
│ AQI Data Processing           │
│ Local Buffering               │
└───────────────┬───────────────┘
                │
                │ MQTT over TLS
                │ QoS 1
                ▼
┌───────────────────────────────┐
│          AWS IoT              │
│                               │
│ MQTT Topic:                   │
│ aqi/sensor/data               │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       AQI Visualization       │
│                               │
│ MQTT Data Monitoring          │
│ Browser-based AQI Dashboard   │
└───────────────────────────────┘

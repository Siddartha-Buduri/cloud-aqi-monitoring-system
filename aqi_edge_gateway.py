import serial
import threading
import time
import re
import json
from collections import deque
from datetime import datetime

import paho.mqtt.client as mqtt


# SERIAL CONFIGURATION

SERIAL_PORT = "COM3"
BAUD_RATE = 115200



# AWS MQTT CONFIGURATION

AWS_ENDPOINT = "YOUR_AWS_IOT_ENDPOINT"
MQTT_PORT = 8883

CLIENT_ID = "AQI_EDGE_NODE"

TOPIC = "aqi/sensor/data"

# Configure these paths locally.
# Do NOT upload certificate/private-key files to GitHub.
ROOT_CA = r"path/to/AmazonRootCA1.pem"
DEVICE_CERT = r"path/to/device-certificate.crt"
PRIVATE_KEY = r"path/to/private-key.key"


# DASHBOARD CONFIGURATION

DISPLAY_COUNT = 5


# LOCAL STORAGE

latest_data = deque(maxlen=DISPLAY_COUNT)


# MQTT CLIENT SETUP

mqtt_client = mqtt.Client(client_id=CLIENT_ID)

mqtt_client.tls_set(
    ca_certs=ROOT_CA,
    certfile=DEVICE_CERT,
    keyfile=PRIVATE_KEY
)


# MQTT CALLBACKS

def on_connect(client, userdata, flags, rc):

    if rc == 0:
        print("\n[AWS MQTT] Connected Successfully\n")
    else:
        print(f"\n[AWS MQTT] Connection Failed : {rc}\n")


mqtt_client.on_connect = on_connect


# CONNECT TO AWS

mqtt_client.connect(AWS_ENDPOINT, MQTT_PORT)

mqtt_client.loop_start()


# MQTT PUBLISHER

def publish_to_aws(payload):

    try:
        message = json.dumps(payload)

        mqtt_client.publish(
            TOPIC,
            message,
            qos=1
        )

        print(
            f"[MQTT SENT] Topic={TOPIC} "
            f"Payload={message}"
        )

    except Exception as e:
        print(f"[MQTT ERROR] {e}")


# SERIAL READER

def serial_reader():

    try:

        ser = serial.Serial(
            SERIAL_PORT,
            BAUD_RATE,
            timeout=1
        )

        print(f"\nConnected to {SERIAL_PORT}\n")

    except Exception as e:

        print(f"Serial Error : {e}")
        return

    current_packet = {}

    while True:

        try:

            line = (
                ser.readline()
                .decode(errors="ignore")
                .strip()
            )

            if not line:
                continue

            print(f"[RAW] {line}")


            # PM2.5

            if "PM2.5 Density:" in line:

                density = re.search(
                    r"PM2\.5 Density:\s*([\d\.]+)",
                    line
                )

                aqi = re.search(
                    r"Sub-AQI:\s*(\d+)",
                    line
                )

                if density:
                    current_packet["pm25_density"] = \
                        float(density.group(1))

                if aqi:
                    current_packet["pm25_aqi"] = \
                        int(aqi.group(1))


            # MQ135

            elif "MQ-135 Voltage:" in line:

                voltage = re.search(
                    r"Voltage:\s*([\d\.]+)",
                    line
                )

                aqi = re.search(
                    r"Est\):\s*(\d+)",
                    line
                )

                if voltage:
                    current_packet["mq135_voltage"] = \
                        float(voltage.group(1))

                if aqi:
                    current_packet["mq135_aqi"] = \
                        int(aqi.group(1))


            # MQ7

            elif "MQ-7" in line:

                voltage = re.search(
                    r"Volts:\s*([\d\.]+)",
                    line
                )

                aqi = re.search(
                    r"Est\):\s*(\d+)",
                    line
                )

                if voltage:
                    current_packet["mq7_voltage"] = \
                        float(voltage.group(1))

                if aqi:
                    current_packet["mq7_aqi"] = \
                        int(aqi.group(1))


            # MQ136

            elif "MQ-136" in line:

                voltage = re.search(
                    r"Volts:\s*([\d\.]+)",
                    line
                )

                aqi = re.search(
                    r"Est\):\s*(\d+)",
                    line
                )

                if voltage:
                    current_packet["mq136_voltage"] = \
                        float(voltage.group(1))

                if aqi:
                    current_packet["mq136_aqi"] = \
                        int(aqi.group(1))


            # MQ131

            elif "MQ-131" in line:

                voltage = re.search(
                    r"Volts:\s*([\d\.]+)",
                    line
                )

                aqi = re.search(
                    r"Est\):\s*(\d+)",
                    line
                )

                if voltage:
                    current_packet["mq131_voltage"] = \
                        float(voltage.group(1))

                if aqi:
                    current_packet["mq131_aqi"] = \
                        int(aqi.group(1))


            # OVERALL AQI

            elif "OVERALL AQI:" in line:

                overall = re.search(
                    r"OVERALL AQI:\s*(\d+)",
                    line
                )

                pollutant = re.search(
                    r"Primary Pollutant:\s*(.*)",
                    line
                )

                if overall:
                    current_packet["overall_aqi"] = \
                        int(overall.group(1))

                if pollutant:
                    current_packet["primary_pollutant"] = \
                        pollutant.group(1)

                current_packet["timestamp"] = \
                    datetime.now().isoformat()


                # SAVE LOCALLY

                received_packet = current_packet.copy()

                latest_data.append(received_packet)

                print(
                    "[RECEIVED VALUES] "
                    f"{json.dumps(received_packet)}"
                )


                # PUBLISH TO AWS

                threading.Thread(
                    target=publish_to_aws,
                    args=(received_packet.copy(),),
                    daemon=True
                ).start()


                # Reset packet
                current_packet = {}


        except Exception as e:

            print(f"[SERIAL ERROR] {e}")


# LIVE TERMINAL DASHBOARD

def dashboard():

    while True:

        print("\033[2J\033[H", end="")

        print("=" * 120)

        print(
            "                AWS AQI EDGE GATEWAY"
        )

        print("=" * 120)


        for idx, data in enumerate(
            reversed(latest_data),
            start=1
        ):

            print(
                f"\n[{idx}] "
                f"{data.get('timestamp')}"
            )

            print(
                f"PM2.5={data.get('pm25_density', '-'):.2f} "
                f"| AQI={data.get('pm25_aqi', '-')}"
            )

            print(
                f"MQ135={data.get('mq135_voltage', '-'):.2f}V "
                f"| MQ7={data.get('mq7_voltage', '-'):.2f}V"
            )

            print(
                f"MQ136={data.get('mq136_voltage', '-'):.2f}V "
                f"| MQ131={data.get('mq131_voltage', '-'):.2f}V"
            )

            print(
                f"OVERALL AQI="
                f"{data.get('overall_aqi', '-')}"
            )

            print(
                f"PRIMARY="
                f"{data.get('primary_pollutant', '-')}"
            )

            print("-" * 120)


        time.sleep(1)


# MAIN

if __name__ == "__main__":

    threading.Thread(
        target=serial_reader,
        daemon=True
    ).start()

    dashboard()

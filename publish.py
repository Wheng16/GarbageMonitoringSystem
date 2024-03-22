# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
import time as t
import json
import random
import schedule
from datetime import datetime, timedelta

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, PATH_TO_AMAZON_ROOT_CA_1, MESSAGE, TOPIC, and RANGE
ENDPOINT = "a3tz9qyn5ip33g-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "testDevice"
PATH_TO_CERTIFICATE = "certificates/b7d9fe24c1d7b18f8001a28a16cf83852c4c83960c8899255c638963adb93efa-certificate.pem.crt"
PATH_TO_PRIVATE_KEY = "certificates/b7d9fe24c1d7b18f8001a28a16cf83852c4c83960c8899255c638963adb93efa-private.pem.key"
PATH_TO_AMAZON_ROOT_CA_1 = "certificates/root.pem"
MESSAGE = "Hello World"
TOPIC = "test/testing"
RANGE = 20

# List of location names and coordinates
locations = [
    {"name": "Universiti Tunku Abdul Rahman (Kampar Campus)", "lat": 4.335050258512359, "lon": 101.13517460896395},
    {"name": "Westlake International School", "lat": 4.33433348269185, "lon": 101.1330073842741},
    {"name": "Westlake Villas Condominium", "lat": 4.327946659077168, "lon": 101.13326487628079},
    {"name": "Westlake Garden", "lat": 4.331423579761355, "lon": 101.13726673193396},
    {"name": "Econsave Kampar", "lat": 4.327518729248778, "lon": 101.14715871876552},
    {"name": "ZUS Coffee Kampar", "lat": 4.326213541868097, "lon": 101.14561376651334},
    {"name": "Grand Kampar", "lat": 4.327593616989616, "lon": 101.14545283400608},
    {"name": "Entertainment Hub", "lat": 4.327387675675965, "lon": 101.14596245370518},
    {"name": "Kampus West City Condominium", "lat": 4.324398976793185, "lon": 101.12970160276119},
    {"name": "Champs Elysees", "lat": 4.322794231255628, "lon": 101.12477706723269}
]

# Function to generate random sensor data for a location
def generate_sensor_data(location):
    bin_id = f"GB{random.randint(1, 100)}"
    fill_level = random.uniform(0, 1)
    temperature = random.uniform(20, 35)
    status = random.choice(["open", "closed", "overflowing"])
    last_pickup = datetime.now() - timedelta(days=random.randint(1, 30))
    ambient_temp = random.uniform(15, 30)
    humidity = random.uniform(0.3, 0.8)
    air_quality = random.randint(50, 100)
    timestamp = datetime.now()

    data = {
        "binId": bin_id,
        "location": {
            "latitude": location["lat"],
            "longitude": location["lon"]
        },
        "fillLevel": fill_level,
        "temperature": temperature,
        "status": status,
        "lastPickupTimestamp": last_pickup.isoformat(),
        "environmentalData": {
            "ambientTemperature": ambient_temp,
            "humidity": humidity,
            "airQuality": air_quality
        },
        "timestamp": timestamp.isoformat()
    }

    return data

# Function to run every 10 seconds
def generate_and_print_data():
    for location in locations:
        sensor_data = generate_sensor_data(location)
        print(f"Sensor data for {location['name']}:")
        print(json.dumps(sensor_data, indent=2))
        print()

# def generate_data():
#     latitude = random.uniform(37.7, 37.8)  # Simulate latitude
#     longitude = random.uniform(-122.5, -122.4)  # Simulate longitude
#     weight = random.uniform(0, 100)  # Simulate weight (in kg)
#     return {"latitude": latitude, "longitude": longitude, "weight": weight}

# Spin up resources
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=ENDPOINT,
            cert_filepath=PATH_TO_CERTIFICATE,
            pri_key_filepath=PATH_TO_PRIVATE_KEY,
            client_bootstrap=client_bootstrap,
            ca_filepath=PATH_TO_AMAZON_ROOT_CA_1,
            client_id=CLIENT_ID,
            clean_session=False,
            keep_alive_secs=6
            )
print("Connecting to {} with client ID '{}'...".format(
        ENDPOINT, CLIENT_ID))
# Make the connect() call
connect_future = mqtt_connection.connect()
# Future.result() waits until a result is available
connect_future.result()
print("Connected!")
# Publish message to server desired number of times.
print('Begin Publish')
# for i in range (RANGE):
#     # data = "{} [{}]".format(MESSAGE, i+1)
#     data = generate_data()
#     message = {"message" : data}
#     mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
#     print("Published: '" + json.dumps(message) + "' to the topic: " + "'test/testing'")
#     t.sleep(0.1)
schedule.every(10).seconds.do(generate_and_print_data)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        t.sleep(1)
print('Publish End')
disconnect_future = mqtt_connection.disconnect()
disconnect_future.result()
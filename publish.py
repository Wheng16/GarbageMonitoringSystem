# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
import time as t
import json
import random
import schedule
from datetime import datetime, timedelta

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, PATH_TO_AMAZON_ROOT_CA_1, and TOPIC
ENDPOINT = "a3tz9qyn5ip33g-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "binsDevice"
PATH_TO_CERTIFICATE = "certificates/ec71681cbc6d795c88583e4f1a5d10c48d47b56825e519c8c84139ad32b205e4-certificate.pem.crt"
PATH_TO_PRIVATE_KEY = "certificates/ec71681cbc6d795c88583e4f1a5d10c48d47b56825e519c8c84139ad32b205e4-private.pem.key"
PATH_TO_AMAZON_ROOT_CA_1 = "certificates/root.pem"
TOPIC = "area-1/garbage-bins-monitoring/"

# List of bin IDs, location names and coordinates
locations = [
    {"binId": 12, "name": "Universiti Tunku Abdul Rahman (Kampar Campus)", "lat": 4.335050258512359, "lon": 101.13517460896395},
    {"binId": 17, "name": "Westlake International School", "lat": 4.33433348269185, "lon": 101.1330073842741},
    {"binId": 22, "name": "Westlake Villas Condominium", "lat": 4.327946659077168, "lon": 101.13326487628079},
    {"binId": 30, "name": "Westlake Garden", "lat": 4.331423579761355, "lon": 101.13726673193396},
    {"binId": 45, "name": "Econsave Kampar", "lat": 4.327518729248778, "lon": 101.14715871876552},
    {"binId": 60, "name": "ZUS Coffee Kampar", "lat": 4.326213541868097, "lon": 101.14561376651334},
    {"binId": 71, "name": "Grand Kampar", "lat": 4.327593616989616, "lon": 101.14545283400608},
    {"binId": 88, "name": "Entertainment Hub", "lat": 4.327387675675965, "lon": 101.14596245370518},
    {"binId": 90, "name": "Kampus West City Condominium", "lat": 4.324398976793185, "lon": 101.12970160276119},
    {"binId": 99, "name": "Champs Elysees", "lat": 4.322794231255628, "lon": 101.12477706723269}
]

# Function to generate random sensor data for a location
def generate_sensor_data(location):
    # bin_id = f"GB{random.randint(1, 100)}"
    fill_level = random.uniform(0, 1) # Fill level of garbage bin, measured as a value between 0 and 1, where 0 represents an empty bin, and 1 represents a completely full bin.
    # temperature = random.uniform(20, 35) # Temperature of garbage bin, measured in degrees Celsius (°C).
    status = random.choice(["open", "closed", "overflowing"]) # Indicates the current state of garbage bin.
    # last_pickup = datetime.now() - timedelta(days=random.randint(1, 30))
    ambient_temp = random.uniform(15, 30) # Temperature of surrounding environment, measured in degrees Celsius (°C).
    humidity = random.uniform(0.3, 0.8) # Amount of water vapor present in the air, measured as a value between 0.3 and 0.8
    air_quality = random.randint(50, 100) # Level of pollutants in the air around the garbage bin, measured as an index value
    timestamp = datetime.now() # Current timestamp

    data = {
        "binId": location["binId"],
        "location": {
            "latitude": location["lat"],
            "longitude": location["lon"]
        },
        "fillLevel": fill_level,
        # "temperature": temperature,
        "status": status,
        # "lastPickupTimestamp": last_pickup.isoformat(),
        "environmentalData": {
            "ambientTemperature": ambient_temp,
            "humidity": humidity,
            "airQuality": air_quality
        },
        "timestamp": timestamp.isoformat()
    }

    return data

def generate_and_transfer_data():
    for location in locations:
        sensor_data = generate_sensor_data(location)
        mqtt_connection.publish(topic=TOPIC+str(sensor_data['binId']), payload=json.dumps(sensor_data), qos=mqtt.QoS.AT_LEAST_ONCE)
        print(f"Sensor data for {location['name']}:")
        print(json.dumps(sensor_data, indent=2))
        print()

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
generate_and_transfer_data()
# schedule.every(10).seconds.do(generate_and_send_data)

# if __name__ == "__main__":
#     while True:
#         schedule.run_pending()
#         t.sleep(1)
print('Publish End')
disconnect_future = mqtt_connection.disconnect()
disconnect_future.result()
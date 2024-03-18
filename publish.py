# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
import time as t
import json
import random

# Define ENDPOINT, CLIENT_ID, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, PATH_TO_AMAZON_ROOT_CA_1, MESSAGE, TOPIC, and RANGE
ENDPOINT = "a3tz9qyn5ip33g-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "testDevice"
PATH_TO_CERTIFICATE = "certificates/b7d9fe24c1d7b18f8001a28a16cf83852c4c83960c8899255c638963adb93efa-certificate.pem.crt"
PATH_TO_PRIVATE_KEY = "certificates/b7d9fe24c1d7b18f8001a28a16cf83852c4c83960c8899255c638963adb93efa-private.pem.key"
PATH_TO_AMAZON_ROOT_CA_1 = "certificates/root.pem"
MESSAGE = "Hello World"
TOPIC = "test/testing"
RANGE = 20

def generate_data():
    latitude = random.uniform(37.7, 37.8)  # Simulate latitude
    longitude = random.uniform(-122.5, -122.4)  # Simulate longitude
    weight = random.uniform(0, 100)  # Simulate weight (in kg)
    return {"latitude": latitude, "longitude": longitude, "weight": weight}

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
for i in range (RANGE):
    # data = "{} [{}]".format(MESSAGE, i+1)
    data = generate_data()
    message = {"message" : data}
    mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
    print("Published: '" + json.dumps(message) + "' to the topic: " + "'test/testing'")
    t.sleep(0.1)
print('Publish End')
disconnect_future = mqtt_connection.disconnect()
disconnect_future.result()
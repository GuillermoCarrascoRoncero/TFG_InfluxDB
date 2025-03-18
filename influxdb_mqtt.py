import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import json

load_dotenv() #variables del .env


# InfluxDB config
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET')  
client = InfluxDBClient(url=os.getenv('INFLUXDB_URL'), 
                        token=os.getenv('INFLUXDB_TOKEN'), 
                        org=os.getenv('INFLUXDB_ORG'))  
write_api = client.write_api()


#MQTT config
MQTT_BROKER_URL = "192.168.1.77"
MQTT_PORT = 1883
MQTT_TOPICS = [("esp8266/angles", 2), ("esp8266/moveServo", 2), ("esp8266/predefinedMovement/request", 2), ("system/metrics", 2)]

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

#Manejo de MQTT
def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Suscripcion rechazada: {reason_code_list[0]}")
    else:
        print(f"Suscripcion completada. QoS: {reason_code_list[0].value}")

def on_unsubscribe(client, userdata, mid, reason_code_list, properties):
    if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
        print("Desuscripcion completada")
    else: 
        print("Error al desuscribirse")
    client.disconnect()

def on_message(client, userdata, message):
    print(f"{message.topic}: {message.payload}")
    topic = message.topic
    payload = message.payload
    data = json.loads(payload)

    if topic == "esp8266/angles":
        angles = data.get("angles", [])
        point = Point("roboticArmAngles").tag("device", "robotic_arm")
        for i, angle in enumerate(angles):
            point = point.field(f"Servo {i}", angle)
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        print("Datos enviados a InfluxDB de /angles")

    elif topic == "esp8266/moveServo":
        angle_value = int(data['angle']) 
        servo_number = data['servo']
        movementName = f"moveServo_{servo_number}"       
        angle_point = Point("roboticArmAngles").tag("device", "robotic_arm").field(f"Servo {servo_number}", angle_value)
        write_api.write(bucket=INFLUXDB_BUCKET, record=angle_point)
        movement_point = Point("roboticArmMovements").tag("device", "robotic_arm").field("Movement",movementName)
        write_api.write(bucket=INFLUXDB_BUCKET, record=movement_point)
        print("Datos enviados a InfluxDB de /moveServo")
    
    elif topic == "esp8266/predefinedMovement/request":
        movementName = data['movement']
        point = Point("roboticArmMovements").tag("device", "robotic_arm").field("Movement",movementName)
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        print("Datos enviados a InfluxDB de /predefinedMovement")

    elif topic == "system/metrics":
        cpuUsage = data['cpuUsage']
        memoryUsed = data['memoryUsed']
        totalUsers = data['totalUsers']    
        point = Point("system").tag("system", "web_server").field("cpuUsage",cpuUsage).field("memoryUsage",memoryUsed).field("totalUsers",totalUsers)
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        print("Datos enviados a InfluxDB de /metrics")

#Conexión MQTT
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Error al conectar: {reason_code}, intentando reconexion")
    else:
        print(f"Conectado a MQTT broker en {MQTT_BROKER_URL}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPICS)

mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_message = on_message
mqttc.on_unsubscribe = on_unsubscribe

#Conexion al broker
try:
    mqttc.connect(MQTT_BROKER_URL, MQTT_PORT)
except Exception as e:
    print(f"Error al conectar al broker MQTT: {e}")
    exit(1)

#Loop mqtt hasta parar el script
try:
    mqttc.loop_forever()
except KeyboardInterrupt:
    mqttc.disconnect()
    print("Desconectado de MQTT")



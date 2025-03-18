# Código Base de Datos

Esta parte del proyecto va dedicado a la implementación de la base de datos en InfluxDB. Una base de datos de series temporales en la que se almacenan el histórico de ángulos del brazo, los movimientos realizados y las métricas de estado del servidor. Para ello se desarrolla un script en Python capacitado para almacenar todas la información recibida desde el servidor MQTT. La configuración tanto de InfluxDB como de Grafana se realiza a través del archivo docker-compose.yaml y un archivo .env,donde se inicializan todas las variables necesarias para su funcionamiento.

## Estructura del código

A través del código `influxdb_mqtt.py` se desarrollo el manejo y almacenamiento de toda la información recibida del servidor web y el controlador del brazo robótico. En el archivo `docker-compose.yaml` se atributen todas las variables iniciales de configuración utilizadas para Docker Compose al incializar la base de datos en InfluxDB y la visualización de cada uno de los datos almacenados en Grafana.




from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
from flask_cors import CORS
import eventlet
eventlet.monkey_patch()  # This ensures compatibility with Flask-SocketIO

app = Flask(__name__)
CORS(app)
# Use Flask-SocketIO with eventlet
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# MQTT Settings
MQTT_BROKER = 'localhost'
MQTT_TOPIC = 'test/topic'

messages = []

# MQTT Callback Functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Message received: {message}")
    messages.append(message)
    socketio.emit('mqtt_message', {'data': message})

# Initialize MQTT Client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, 1883, 60)
mqtt_client.loop_start()

@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    return response

@app.route('/')
def index():
    return render_template('lig.html')

@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify(messages)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)

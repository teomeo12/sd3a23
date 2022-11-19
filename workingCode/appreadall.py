from flask import Flask, redirect, render_template, request, session
import json
import RPi.GPIO as GPIO
import time, threading
import board
import adafruit_dht
import board
import busio
import time
from time import sleep
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

from flask_session import Session
from flask_mysqldb import MySQL

from dotenv import load_dotenv
import os

app = Flask(__name__)
# Database

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = 'GMS'

print(os.getenv('MYSQL_USER'))

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

mysql = MySQL(app)
# Setup motion sensor and buzzer pins output
alive = 0
data = {}
PIR_pin = 23
Buzzer_pin = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_pin, GPIO.IN)
GPIO.setup(Buzzer_pin, GPIO.OUT)

# GPIO SETUP temperature and humidity pins output
tmp_sensor = adafruit_dht.DHT11(board.D17)
moist_pin = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(moist_pin, GPIO.IN)

# Setup The Ph sensor pins output
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
channel = AnalogIn(ads, ADS.P0)  # Use channel 0 to measure the voltage

# SETUP for pump2
in1 = 5
in2 = 6
en = 26
temp1 = 1

GPIO.setmode(GPIO.BCM)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(en, GPIO.OUT)
GPIO.output(in1, GPIO.LOW)
GPIO.output(in2, GPIO.LOW)
p = GPIO.PWM(en, 1000)

p.start(100)
print("\n")



def read_data():  # Function to read the Ph value
    while True:
        buf = list()

        for i in range(10):  # Take 10 samples
            buf.append(channel.voltage)
        buf.sort()  # Sort samples and discard highest and lowest
        buf = buf[2:-2]  # skip the first two and the last two values
        avg = (sum(map(float, buf)) / 6)  # Get average value from remaining 6 values

        ph_val = (-7.119047 * avg) + (29.14023)  # Calculate the Ph value from the given voltage

        print("avg V: ", round(avg, 2))
        print("Ph Buf: ", round(ph_val, 2))
        print()
        time.sleep(2)

        # TODO if the ph is under value run the pump
        # while True:
        try:
            temp = tmp_sensor.temperature
            temp_f = temp * (9 / 5) + 32
            humidity = tmp_sensor.humidity
            print("Temp: {:.1f} C / {:.1f} F    Humidity: {}% "
                  .format(temp, temp_f, humidity))
            if GPIO.input(moist_pin):
                print("The soil is dry!")
            else:
                print("The soil is wet!")



        except RuntimeError as error:
            print(error.args[0])
            time.sleep(2.0)
            # continue
        except Exception as error:
            tmp_sensor.exit()
            raise error
        time.sleep(2.0)
        #Motion sensor

        def beep(repeat):
            for i in range(0, repeat):
                for pulse in range(60):
                    GPIO.output(Buzzer_pin, True)
                    time.sleep(0.001)
                    GPIO.output(Buzzer_pin, False)
                    time.sleep(0.001)
                time.sleep(0.02)

        data["alarm"] = False
        # while True:
        if (GPIO.input(PIR_pin)):
            print("Motion detected!")
            beep(4)
            data["motion"] = 1
        else:
            data["motion"] = 0
            print("No motion")
        if data["alarm"]:
            beep(2)
            print("Turning on the buzzer from index.html")
        time.sleep(1)




@app.route("/")
def index():
    return render_template("index.html")


@app.route("/keep_alive")
def keep_alive():
    global alive, data
    alive += 1
    keep_alive_count = str(alive)
    data['keep_alive'] = keep_alive_count
    parsed_json = json.dumps(data)
    print(parsed_json)
    return str(parsed_json)


@app.route("/status=<name>-<action>", methods=["POST"])
def event(name, action):
    global data
    print("Got: " + name + ", action" + action)
    if name == "buzzer":
        if action == "ON":
            data["alarm"] = True
        elif action == "OFF":
            data["alarm"] = False
    return str("OK")


if __name__ == '__main__':


    # sensors_thread = threading.Thread(target=motion_detection)
    # sensors_thread = threading.Thread(target=read_temp)
    sensors_thread = threading.Thread(target=read_data())

    sensors_thread.start()
    app.run(host="192.168.8.130", port=5000)
    # app.run(host="10.108.4.227", port=5000)

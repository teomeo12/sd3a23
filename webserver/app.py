from flask import Flask, render_template
import json
import RPi.GPIO as GPIO
import time, threading
import board
import adafruit_dht
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory, PNOperationType
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

pnconfig = PNConfiguration()
pnconfig.cipher_key = 'myCipherKey'
pnconfig.subscribe_key = 'sub-c-5832596e-d4b6-4552-b2c0-a28a18fadd40'
pnconfig.publish_key = 'pub-c-dab1a887-ba42-48aa-b99d-e42ecf3dedb3'
pnconfig.user_id = "my_custom_user_id"
pubnub = PubNub(pnconfig)

my_channel = 'teo-channel'
sensors_list = ["buzzer"]
data = {}

def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];
class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass  # handle incoming presence data
    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass  # This event happens when radio / connectivity is lost
        elif status.category == PNStatusCategory.PNConnectedCategory:
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            pubnub.publish().channel(my_channel).message('Hello world!').pn_async(my_publish_callback)
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            pass
            # Happens as part of our regular operation. This event happens when
            # radio / connectivity is lost, then regained.
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass
            # Handle message decryption error. Probably client configured to
            # encrypt messages and on live data feed it received plain text.
    def message(self, pubnub, message):
        # Handle new message stored in message.message
        print(message.message)


app = Flask(__name__)

alive = 0
data = {}
PIR_pin = 23
Buzzer_pin = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_pin, GPIO.IN)
GPIO.setup(Buzzer_pin, GPIO.OUT)

#GPIO SETUP
tmp_sensor = adafruit_dht.DHT11(board.D17)
moist_pin = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(moist_pin, GPIO.IN)

def read_temp():
    #temp_data["temp"] = 0
    while True:
        try:
            temp = tmp_sensor.temperature
            temp_f = temp * (9 / 5) + 32
            humidity = tmp_sensor.humidity
            print("Temp: {:.1f} C / {:.1f} F    Humidity: {}% "
                   .format(temp, temp_f, humidity))
            #temp_data["temp"] = temp
            #publish(myChannel, {'temp':{'tempC':temp}, 'hum' :{'hum':humidity})
            if GPIO.input(moist_pin):
                print ("dry!")
            else:
                print ("wet!")

        except RuntimeError as error:
            print(error.args[0])
            time.sleep(2.0)
            continue
        except Exception as error:
            tmp_sensor.exit()
            raise error
        time.sleep(2.0)

def beep(repeat):
    for i in range(0, repeat):
        for pulse in range(60):
            GPIO.output(Buzzer_pin, True)
            time.sleep(0.001)
            GPIO.output(Buzzer_pin, False)
            time.sleep(0.001)
        time.sleep(0.02)

def motion_detection():
    data["alarm"] = False
    while True:
        if(GPIO.input(PIR_pin)):
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

def temp_hum():
    global temp_data
    parsed_json = json.dumps(temp_data)
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
    # Publish the data with PubNub
    pubnub.add_listener(MySubscribeCallback())
    pubnub.subscribe().channels(my_channel).execute()
    time.sleep(3)
    
    motion_thread_1 = threading.Thread(target=motion_detection)
    motion_thread_1.start()

    dht_thread_2 = threading.Thread(target=read_temp)
    dht_thread_2.start()
    # Start the threads



    #start the web server
    app.run(host="192.168.8.130", port=5000)
    # app.run(host="10.108.4.227", port=5000)

    # Run all the thread one after another
    motion_thread_1 .join()
    dht_thread_2.join()




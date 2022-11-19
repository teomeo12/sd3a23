import RPi.GPIO as GPIO
import time
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory, PNOperationType
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import time, threading

pnconfig = PNConfiguration()
pnconfig.subscribe_key= 'sub-c-5832596e-d4b6-4552-b2c0-a28a18fadd40'
pnconfig.publish_key= 'pub-c-dab1a887-ba42-48aa-b99d-e42ecf3dedb3'

pnconfig.user_id='teo-pi-4'
pubnub = PubNub(pnconfig)
#imports for dht11
import time
import board
import adafruit_dht
import psutil

PIR_pin =23
Buzzer_pin =24

my_channel = 'teo-pi-channel'
sensors_list = ["buzzer"]
data ={}

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
def publish(channel,message):
    pubnub.publish().channel(channel).message(message).pn_async(my_publish_callback)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
#signal for PIR sensor
GPIO.setup(PIR_pin, GPIO.IN)
#signal out for buzzer and LED
GPIO.setup(Buzzer_pin, GPIO.OUT)
#check wheter the request was successfuly completed

# We first check if a libgpiod process is running. If yes, we kill it!
for proc in psutil.process_iter():
    if proc.name() == 'libgpiod_pulsein' or proc.name() == 'libgpiod_pulsei':
        proc.kill()
sensor = adafruit_dht.DHT11(board.D17)


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
    trigger = False
    while(True):
        if GPIO.input(PIR_pin):
            print("Intrudern detected")
            beep(4)
            trigger = True
            publish(my_channel,{"motion":"Yes"})
            time.sleep(1)
            
        elif trigger:
            publish(my_channel,{"motion":"No"})
            trigger = True
        if data["alarm"]:
            beep(3)
                     
        else:               
            print ("No intruders")
            
        time.sleep(1)

if __name__ == '__main__':
    sensors_thread = threading.Thread(target=motion_detection)
    sensors_thread.start()
    #app.run(host="192.168.8.130", port=5000)
    #app.run(host="10.106.2.119", port=5000)
    pubnub.add_listener(MySubscribeCallback())
    pubnub.subscribe().channels(my_channel).execute()

#time.sleep(1)
#motion_detection()
#time.sleep(1)





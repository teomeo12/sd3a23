#!/usr/bin/python
''' Raspberry Pi, ADS1115, PH4502C Calibration '''
import board
import busio
import time
import sys
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Setup 
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)


def read_voltage(channel):# Function to read the voltage of the channel
    while True:
        buf = list()
        
        for i in range(10): # Take 10 samples
            buf.append(channel.voltage)
        buf.sort() # Sort samples and discard highest and lowest
        buf = buf[2:-2] # skip the first two and the last two values
        avg = (sum(map(float, buf))/6) # Get average value from remaining 6 values

        ph_val = (-7.119047 * avg) + (29.14023) # Calculate the Ph value from the given voltage

        print("avg V: ", round(avg, 2))
        print("Ph Buf: ", round(ph_val, 2))
        print()
        time.sleep(2)


if __name__ == '__main__':
    print('\n\n\n')
    print('---- RPi-ADS115-PH4502 Calibration ----')
    input('Press Enter once you have grounded the BNC connector...')
#     channel = 0
#     while channel not in [0,1,2,3]:
#         try: 
#             channel = int(input('ADS1115 channel 0-3: '))  # ADS.P0, ADS.P1, ADS.P2, ADS.P3
#         except:
#             print('Not a valid option. Try again.')
#     if channel == 0:
#         channel = AnalogIn(ads, ADS.P0)
#         print("chanel 1")
#     
#     else:
#         sys.exit('Error selecting an ADS1115 pin.')
#     print('Adjust potentiometer nearest to BNC socket to ~2.50V')
#     print('Starting readings. Press CTRL+C to stop...')
#     
    channel = AnalogIn(ads, ADS.P0)
    try:
        read_voltage(channel)
    except KeyboardInterrupt:
        pass

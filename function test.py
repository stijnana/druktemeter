from Adafruit_IO import *
import RPi.GPIO as GPIO
import time as yotimma
import numpy as np
import sounddevice as sd

aio = Client('Nizari' , 'aio_rsem169oLOMV5K89rjq9Unaut2dB')

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
PIR_PIN = 3
GPIO.setup(PIR_PIN, GPIO.IN)

print('Starting up the PIR Module (click on STOP to exit)')
print('Ready')

totalDb = []

duration = 3 #in seconds
aio = Client('Nizari' , 'aio_rsem169oLOMV5K89rjq9Unaut2dB')

def audio_callback(indata, frames, time, status):
    volume_norm = np.linalg.norm(indata) * 10
    volume_norm = int(volume_norm)
    totalDb.append(volume_norm)
    print(volume_norm)
    
    

def send_data(dbArray):
    length = len(dbArray)
    total = sum(dbArray)
    
    average = total / length
    
    averageRound = int(average)
    aio.send("sound-levels", int(averageRound))

    totalDb.clear()
    
    
    
while True:
  if GPIO.input(PIR_PIN):
    print('Motion Detected')
    stream = sd.InputStream(callback=audio_callback)
    with stream:
        sd.sleep(duration * 1000)
    send_data(totalDb)
  else:
    print('No Motion Detected')
    aio.send("sound-levels", 0)
    
    yotimma.sleep(3)
  yotimma.sleep(1)
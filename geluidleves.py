from Adafruit_IO import *
import RPi.GPIO as GPIO
import time as yotimma
import numpy as np
import sounddevice as sd

#Connectie met de adafruit api
aio = Client('Nizari' , '')

#setten van de pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
PIR_PIN = 3
GPIO.setup(PIR_PIN, GPIO.IN)

#print dat de code ready is
print('Starting up the PIR Module (click on STOP to exit)')
print('Ready')

totalDb = []


#over hoeveel tijd wil je het gemidelde pakken van hoe druk het is
duration = 3 #in seconds


#functie die ophaalt wat de geluids levels zijn
def audio_callback(indata, frames, time, status):
    volume_norm = np.linalg.norm(indata) * 10
    volume_norm = int(volume_norm)
    totalDb.append(volume_norm)
    print(volume_norm)
    
    
#send via de adafuit api data naar het dashboard
def send_data(dbArray):
    length = len(dbArray)
    total = sum(dbArray)
    
    average = total / length
    
    averageRound = int(average)
    aio.send("sound-levels", int(averageRound))

    totalDb.clear()
    
     
#de check of er beweging is te zien voor de sensoren als er beweging is erkent start hij de opnamen van een gemidlde geluids levels  
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

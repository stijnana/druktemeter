#import
import RPi.GPIO as GPIO
from Adafruit_IO import *
import struct
import time
from time import gmtime, strftime
import datetime

#set var voor welken geluid leves nodig zijn om de lampjes aan te doen
greenLed = 10
blueLed = 20
redLed = 60

#set de var voor de aio client
aio = Client('Nizari', 'aio_rsem169oLOMV5K89rjq9Unaut2dB')

#ophalen van de locatie data
locationOne = aio.receive_previous('location')

print(format(locationOne.value))


#functie om de huidige tijd op te halen
def printDateTime():
  textTime = strftime("%H:%M")
  print ('time updated')
  lcd_string(format(locationOne.value),LCD_LINE_1)
  lcd_string(textTime ,LCD_LINE_2)
  return

#led interface mapping
def getInterfaceAddress(ifname):
  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
      s.fileno(),
      0x8915,  # SIOCGIFADDR
      struct.pack('256s', ifname[:15])
    )[20:24])
  except:
    return ''


#Pin mapping
LCD_RS = 26
LCD_E  = 19
LCD_D4 = 0 #13
LCD_D5 = 6
LCD_D6 = 5
LCD_D7 = 11


#Def van de dicplay zoals char limit
LCD_WIDTH = 16    #max chars per line
LCD_CHR = True
LCD_CMD = False
#Def van de lines van de display
LCD_LINE_1 = 0x80 #line 1 display
LCD_LINE_2 = 0xC0 #line 2 dicplay

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

def main():

  
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)     
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7


  lcd_init()

  while True:
    CollectDbData()

    # Display date and time
    index = 0
    while index < 10:
      printDateTime()
      time.sleep(1)
      index += 1

#functie voor het ophalen van de data vannuit adafruit van de laaste 5 minuten
def CollectDbData():
    AveArray = []
    data = aio.data('sound-levels')
    CurTime = datetime.datetime.now()
    SubTime = datetime.timedelta(minutes=65)
    NewTime = CurTime - SubTime
    NewTime = NewTime.strftime("%Y-%m-%d %H:%M:%S")
    NewTime = datetime.datetime.strptime(NewTime, "%Y-%m-%d %H:%M:%S")
#goed zetten van de tijd vanuit adafruit zodat we het kunnen vergelijken
    for d in data:
        SoundVal = format(d.value)
        TimeVal = format(d.created_at)
        TimeVal = TimeVal.replace("T", " ")
        TimeVal = TimeVal.replace("Z", "")
        TimeVal = datetime.datetime.strptime(TimeVal, "%Y-%m-%d %H:%M:%S")
        
        was_date1_before = TimeVal > NewTime
        
        if was_date1_before:
            AveArray.append(SoundVal)
    for i in range(0, len(AveArray)):
        AveArray[i] = int(AveArray[i])
    
	#het berekenen van de gemiddelde van de afgelopen 5 minuten
    length = len(AveArray)
    total = sum(AveArray)
    averageRound = 0
    if length > 0:
        average = total / length
        averageRound = int(average)
    
    print(averageRound)
    GPIO.setmode(GPIO.BCM)
    
    GPIO.setwarnings(False)
    GPIO.setup(RED,GPIO.OUT)
    GPIO.output(RED,0)
    GPIO.setup(GREEN,GPIO.OUT)
    GPIO.output(GREEN,0)
    GPIO.setup(BLUE,GPIO.OUT)
    GPIO.output(BLUE,0)
    
	#lampjes aan en uit zetten aan de hand van de laaste 5 minuten
    print (averageRound)
    if averageRound <= greenLed:
        GPIO.output(RED,100)
        GPIO.output(GREEN,0)
        GPIO.output(BLUE,100)
        
    if averageRound > greenLed and averageRound <= blueLed:
        GPIO.output(RED,100)
        GPIO.output(GREEN,100)
        GPIO.output(BLUE,0)
        
    if averageRound > redLed:
        GPIO.output(RED,0)
        GPIO.output(GREEN,100)
        GPIO.output(BLUE,100)


    #time.sleep(60)



#code vanuit een lib voor het instellen van de display
def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Cast to string
  message = str(message)
  # Send string to display
  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Goodbye!",LCD_LINE_1)
    GPIO.cleanup()

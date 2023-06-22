import board
import audiomp3
import audiobusio
import digitalio
import busio
import adafruit_si4713
import simpleio
import time
import i2c_pcf8574_interface
import lcd

FREQUENCY_KHZ = 107500

OnAirled = digitalio.DigitalInOut(board.GP8)
Lockedled = digitalio.DigitalInOut(board.GP9)
Clipled = digitalio.DigitalInOut(board.GP10)
Failureled = digitalio.DigitalInOut(board.GP11)
Initled = digitalio.DigitalInOut(board.GP12)
Overloaddled = digitalio.DigitalInOut(board.GP13)

OnAirled.direction = digitalio.Direction.OUTPUT
Lockedled.direction = digitalio.Direction.OUTPUT
Clipled.direction = digitalio.Direction.OUTPUT
Failureled.direction = digitalio.Direction.OUTPUT
Initled.direction = digitalio.Direction.OUTPUT
Overloaddled.direction = digitalio.Direction.OUTPUT

OnAirled.value = False
Lockedled.value = False
Clipled.value = False
Failureled.value = False
Initled.value = False
Overloaddled.value = False
time.sleep(1)
OnAirled.value = True
Lockedled.value = True
Clipled.value = True
Failureled.value = True
Initled.value = True
Overloaddled.value = True
time.sleep(1)
OnAirled.value = False
Lockedled.value = False
Clipled.value = False
Failureled.value = False
Initled.value = True
Overloaddled.value = False

simpleio.tone(board.GP4, 1500, duration=0.1)
print("[system] initializing i2c")
try:
    i2c = busio.I2C(board.GP7, board.GP6)
    simpleio.tone(board.GP4, 1000, duration=0.1)
    print("[system] initialized i2c")
except Exception as e:
    simpleio.tone(board.GP4, 440, duration=0.1)
    print("[system] initializing i2c failed")
    print(e)
    time.sleep(1)
    
simpleio.tone(board.GP4, 540, duration=0.1)
print("[system] initializing esp8266")
try:
    esp8266 = busio.UART(board.GP0, board.GP1, baudrate=9600)
    simpleio.tone(board.GP4, 1000, duration=0.1)
    print("[system] initialized esp8266")
except Exception as e:
    simpleio.tone(board.GP4, 440, duration=0.1)
    print("[system] initializing esp8266 failed")
    print(e)
    time.sleep(1)
   
"""
simpleio.tone(board.GP4, 2000, duration=0.1)
print("[system] initializing lcd")
try:
    i2clcd = i2c_pcf8574_interface.I2CPCF8574Interface(i2c, 0x27)
    display = lcd.LCD(i2clcd, num_rows=2, num_cols=16)
    display.set_backlight(True)
    display.set_display_enabled(True)
    print("[system] initialized lcd")
except Exception as e:
    simpleio.tone(board.GP4, 440, duration=0.1)
    print("[system] initializing lcd failed")
    print(e)
    time.sleep(1)
"""

simpleio.tone(board.GP4, 500, duration=0.1)
print("[system] initializing si4713 instance")
try:
    si_reset = digitalio.DigitalInOut(board.GP3)
    si4713 = adafruit_si4713.SI4713(i2c, reset=si_reset, timeout_s=0.5)
    print("[system] initialized si4713 instance")
    simpleio.tone(board.GP4, 1000, duration=0.1)
except Exception as e:
    simpleio.tone(board.GP4, 440, duration=0.1)
    print("[system] initializing si4713 failed")
    print(e)
    time.sleep(1)

"""
display.clear()
display.print("Welcome")
time.sleep(1)
display.clear()
display.print("FM Transmitter\nV1.0")
time.sleep(1)


for i in reversed(range(1, 4)):
    display.clear()
    display.print(f"Starting in {i}")
    time.sleep(1)
"""

try:
    noise = si4713.received_noise_level(FREQUENCY_KHZ)
    print("[SI4713] Noise at {0:0.3f} mhz: {1} dBuV".format(FREQUENCY_KHZ / 1000.0, noise))

    si4713.tx_frequency_khz = FREQUENCY_KHZ
    si4713.tx_power = 115

    si4713.configure_rds(0x27C8, station=b"HSA62BFM", rds_buffer=b"")

    print("[SI4713] Transmitting at {0:0.3f} mhz".format(si4713.tx_frequency_khz / 1000.0))
    print("[SI4713] Transmitter power: {0} dBuV".format(si4713.tx_power))
    print("[SI4713] Transmitter antenna capacitance: {0:0.2} pF".format(si4713.tx_antenna_capacitance))

    print("[SI4713] Broadcasting...")
    
    esp8266.write(bytes(f"txfreq {si4713.tx_frequency_khz / 1000.0}\n", 'utf-8'))
    esp8266.write(bytes(f"txpower {si4713.tx_power}\n", 'utf-8'))
    esp8266.write(bytes(f"txantennacap {si4713.tx_antenna_capacitance}\n", 'utf-8'))
    
    #display.clear()
    #display.print(f"Broadcasting...\nOn Air on {FREQUENCY_KHZ/1000}")
    
    OnAirled.value = True
    Initled.value = False
    
except Exception as e:
    Failureled.value = True
    simpleio.tone(board.GP4, 440, duration=0.1)
    print(e)

while not i2c.try_lock():
    pass

while True:
    i2c.writeto(0x63, bytes([0x13]))
    data = bytearray(1)
    i2c.readfrom_into(0x63, data)
    if (data[0] >> 7) == 1:
        print("[SI4713] PLL locked!")
        Lockedled.value = True
        break

i2c.unlock()

try:
    while True:
        try:
            if esp8266.in_waiting > 0:
                data = esp8266.read(150)
                
                print(data)
                
                data = data.decode("utf-8").split("|")[0]
                
                print(data)
                
                try:
                    if data.startswith("!setrdsbuffer "):
                        print(bytes(data.split("!setrdsbuffer ")[1], "utf-8"))
                        si4713.rds_buffer = bytes(data.split("!setrdsbuffer ")[1], "utf-8")
                    elif data.startswith("!setrdstation "):
                        si4713.rds_station = bytes(data.split("!setrdstation ")[1], "utf-8")
                    elif data.startswith("!setgentxpower "):
                        si4713.tx_power = int(data.split("!setgentxpower ")[1])
                    elif data.startswith("!settxfreq "):
                        si4713.tx_frequency_khz = int(data.split("!settxfreq ")[1])
                except Exception as e:
                    print(e)
        except Exception as e:
                print(e)
        input_level = si4713.input_level
        audio_signal_status = si4713.audio_signal_status
        #print("[SI4713] Input level: {0} dBfs".format(input_level))
        #print("[SI4713] ASQ status: 0x{0:02x}".format(audio_signal_status))
        esp8266.write(bytes(f"INLE {input_level}\n", 'utf-8'))
        esp8266.write(bytes(f"ASQ {audio_signal_status}\n", 'utf-8'))
        
        #display.clear()
        #display.print(f"Input level: {input_level} dBfs")
        
        if input_level == 0 and audio_signal_status == 0x04:
            print("[SI4713] Overloaded!!")
            esp8266.write(bytes(f"ASQW Overloaded\n", 'utf-8'))
            Overloaddled.value = True
        else:
            Overloaddled.value = False
            
        if input_level == 0 and audio_signal_status == 0x00:
            print("[SI4713] Clip!!")
            esp8266.write(bytes(f"ASQW Clip\n", 'utf-8'))
            Clipled.value = True
        else:
            Clipled.value = False
            
        
        time.sleep(0.1)
        
except Exception as e:
    Failureled.value = True
    simpleio.tone(board.GP4, 440, duration=0.1)
    print(e)
    if e == "[system] [Errno 19] No such device":
        OnAirled.value = False


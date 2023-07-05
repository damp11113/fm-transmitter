import board
import digitalio
import busio
import adafruit_si4713
import simpleio
import time
import i2c_pcf8574_interface
# import si4713_addons
import lcd

from micropython import const

_SI4713_PROP_TX_RDS_PS_MISC = const(0x2C03)
_SI4713_PROP_TX_COMPONENT_ENABLE = const(0x2100)
_SI4713_PROP_TX_LINE_INPUT_MUTE = const(0x2105)
_SI4713_PROP_TX_ACOMP_THRESHOLD = const(0x2201)
_SI4713_PROP_TX_ACOMP_ENABLE = const(0x2200)

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

def pad_with_zeros(number, width):
    padded_number = "0" * (width - len(str(number))) + str(number)
    return padded_number

class Settings:
    def __init__(self):
        # more info https://en.wikipedia.org/wiki/Radio_Data_System
        # general
        self.stereo = True
        self.power = 115
        self.frequency_khz = 107500
        self.compressed = 0x0000
        self.ACEN = False
        # RDS
        self.RDS = True
        self.RDSpicode = 0x27C8
        self.RDSps = b"HSA62BFM"
        self.RDSrt = b""
        self.RDSpty = 9
        self.RDSdynamicpty = True
        self.RDStp = False
        self.RDSartificialhead = False
        self.RDSforceb = False
        self.RDSta = False
        self.RDSms = False
        # other
        self.PLLchecksec = 5

    def getData(self):
        data = []
        for var_name, var_value in self.__dict__.items():
            if isinstance(var_value, bytes):
                var_value = var_value.decode('utf-8')  # Assuming utf-8 encoding, change if necessary
            data.append((var_name, var_value))
        return data

    def _RDSmiscgen(self, stereo=False, artificialhead=False, compressed=False, dynamicpty=False, tp=False, pty=0,
                    forceb=False, ta=False, ms=False):
        # Construct the 16-bit value
        value = (int(stereo) << 15) | (int(artificialhead) << 14) | (int(compressed) << 13) | (
                int(dynamicpty) << 12) | (int(forceb) << 11) | \
                (int(tp) << 10) | (pty << 5) | (int(ta) << 4) | (int(ms) << 3)

        # Convert the value to hex
        hex_code = pad_with_zeros(hex(value)[2:].upper(), 4)

        return int(hex_code, 16)

    def StereoRDSswitch(self):
        time.sleep(0.1)
        print(self.stereo, self.RDS)
        if self.stereo is False and self.RDS:
            si4713.setProperty(_SI4713_PROP_TX_COMPONENT_ENABLE, 0x04)  # mono and RDS
        elif self.stereo and self.RDS:
            si4713.setProperty(_SI4713_PROP_TX_COMPONENT_ENABLE, 0x07)  # stereo and RDS
        elif self.stereo is False and self.RDS is False:
            si4713.setProperty(_SI4713_PROP_TX_COMPONENT_ENABLE, 0x00)  # mono only
        elif self.RDS is False:
            si4713.setProperty(_SI4713_PROP_TX_COMPONENT_ENABLE, 0x03)  # stereo only

    def SInit(self):
        si4713.tx_frequency_khz = settings.frequency_khz
        si4713.tx_power = 88
        si4713.setProperty(_SI4713_PROP_TX_LINE_INPUT_MUTE, 0x03)
        si4713.setProperty(_SI4713_PROP_TX_ACOMP_THRESHOLD, self.compressed)
        if self.compressed == 0x0000:
            limit = False
        else:
            limit = True
            
        if limit and self.ACEN:
            si4713.setProperty(_SI4713_PROP_TX_ACOMP_ENABLE, 0x0003)
        elif limit and not self.ACEN:
            si4713.setProperty(_SI4713_PROP_TX_ACOMP_ENABLE, 0x0002)
        elif not limit and self.ACEN:
            si4713.setProperty(_SI4713_PROP_TX_ACOMP_ENABLE, 0x0001)
        elif not limit and not self.ACEN:
            si4713.setProperty(_SI4713_PROP_TX_ACOMP_ENABLE, 0x0000)

        if settings.RDS:
            si4713.configure_rds(self.RDSpicode, station=self.RDSps, rds_buffer=self.RDSrt)
            self.updateRDSmisc()
        
        self.StereoRDSswitch()

    def updateRDSmisc(self):
        if self.compressed == 0x0000:
            RDScompressed = False
        else:
            RDScompressed = True
        hex = self._RDSmiscgen(self.stereo, self.RDSartificialhead, RDScompressed, self.RDSdynamicpty,
                                            self.RDStp, self.RDSpty, self.RDSforceb, self.RDSta, self.RDSms)
        si4713.setProperty(_SI4713_PROP_TX_RDS_PS_MISC, hex)


settings = Settings()

try:
    noise = si4713.received_noise_level(settings.frequency_khz)
    print("[SI4713] Noise at {0:0.3f} mhz: {1} dBuV".format(settings.frequency_khz / 1000.0, noise))

    settings.SInit()
    
    for option, value in settings.getData():
        esp8266.write(bytes(f"{option} {value}\n", 'utf-8'))
        time.sleep(0.1)

    # for i in range(88, 116):
    #    print(i)
    #    si4713.tx_power = i
    #    time.sleep(0.1)

    # si4713.setProperty(_SI4713_PROP_TX_COMPONENT_ENABLE, 0x07)  # stereo and RDS
    # si4713.setProperty(_SI4713_PROP_TX_COMPONENT_ENABLE, 0x06) # mono, stereo L-R and RDS
    # si4713.setProperty(_SI4713_PROP_TX_COMPONENT_ENABLE, 0x05) # mono, pilot and RDS
    # si4713.setProperty(_SI4713_PROP_TX_COMPONENT_ENABLE, 0x04) # mono and RDS
    # si4713.setProperty(_SI4713_PROP_TX_COMPONENT_ENABLE, 0x03) # stereo only
    # si4713.setProperty(_SI4713_PROP_TX_COMPONENT_ENABLE, 0x02) # mono and stereo L-R
    # si4713.setProperty(_SI4713_PROP_TX_COMPONENT_ENABLE, 0x01) # mono and pilot
    # si4713.setProperty(_SI4713_PROP_TX_COMPONENT_ENABLE, 0x00) # mono only

    # si4713.setProperty(_SI4713_PROP_TX_RDS_PS_MISC, 0x9120)

    print("[SI4713] Transmitting at {0:0.3f} mhz".format(settings.frequency_khz / 1000.0))
    print("[SI4713] Transmitter power: {0} dBuV".format(settings.power))
    print("[SI4713] Transmitter antenna capacitance: {0:0.2} pF".format(si4713.tx_antenna_capacitance))

    print("[SI4713] Broadcasting...")

    esp8266.write(bytes(f"txfreq {settings.frequency_khz / 1000.0}\n", 'utf-8'))
    esp8266.write(bytes(f"txpower {settings.power}\n", 'utf-8'))
    esp8266.write(bytes(f"txantennacap {si4713.tx_antenna_capacitance}\n", 'utf-8'))

    # display.clear()
    # display.print(f"Broadcasting...\nOn Air on {FREQUENCY_KHZ/1000}")

    OnAirled.value = True
    Initled.value = False

except Exception as e:
    Failureled.value = True
    simpleio.tone(board.GP4, 440, duration=0.1)
    print(e)

for i in reversed(range(settings.PLLchecksec)):
    time.sleep(1)

print("[SI4713] PLL locked!")
Lockedled.value = True
si4713.setProperty(_SI4713_PROP_TX_LINE_INPUT_MUTE, 0x00)
si4713.tx_power = settings.power

try:
    while True:
        if esp8266.in_waiting > 0:
            try:
                data = esp8266.read(200).decode("utf-8")

                print("[ESP8266] " + data)
                    
                data = data.split("|")[0]
            
                print("[ESP8266 command] " + data)

                try:
                    if data.startswith("!setrdsbuffer "):
                        si4713.rds_buffer = bytes(data.split("!setrdsbuffer ")[1].replace("+", " "), "utf-8")
                    elif data.startswith("!setrdstation "):
                        si4713.rds_station = bytes(data.split("!setrdstation ")[1], "utf-8")
                    elif data.startswith("!setgentxpower "):
                        si4713.tx_power = int(data.split("!setgentxpower ")[1])
                    elif data.startswith("!settxfreq "):
                        si4713.tx_frequency_khz = int(data.split("!settxfreq ")[1])
                    elif data.startswith("!getdata "):
                        for option, value in settings.getData():
                            esp8266.write(bytes(f"{option} {value}\n", 'utf-8'))
                            time.sleep(0.1)
                    elif data.startswith("!setrdspty "):
                        settings.RDSpty = int(data.split("!setrdspty ")[1])
                        settings.updateRDSmisc()
                    elif data.startswith("!setaudiochannel "):
                        data = data.split("!setaudiochannel ")[1]
                        if data == "mono":
                            settings.stereo = False
                        elif data == "stereo":
                            settings.stereo = True
                        settings.updateRDSmisc()
                        settings.StereoRDSswitch()
                    elif data.startswith("!setrds "):
                        data = data.split("!setrds ")[1]
                        print(data)
                        if data == "enable":
                            settings.RDS = True
                        elif data == "disable":
                            settings.RDS = False
                        settings.StereoRDSswitch()


                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)
        input_level = si4713.input_level
        audio_signal_status = si4713.audio_signal_status
        # print("[SI4713] Input level: {0} dBfs".format(input_level))
        # print("[SI4713] ASQ status: 0x{0:02x}".format(audio_signal_status))
        esp8266.write(bytes(f"INLE {input_level}\n", 'utf-8'))
        esp8266.write(bytes(f"ASQ {audio_signal_status}\n", 'utf-8'))

        # display.clear()
        # display.print(f"Input level: {input_level} dBfs")

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

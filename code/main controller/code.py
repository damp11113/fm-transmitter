import board
import digitalio
import busio
import adafruit_si4713
import simpleio
import time
#import i2c_pcf8574_interface
#import lcd
#import microcontroller

from micropython import const

_SI4713_PROP_TX_RDS_PS_AF = const(0x2C06)
_SI4713_PROP_TX_RDS_PS_MISC = const(0x2C03)
_SI4713_PROP_TX_COMPONENT_ENABLE = const(0x2100)
_SI4713_PROP_TX_LINE_INPUT_MUTE = const(0x2105)
_SI4713_PROP_TX_ACOMP_THRESHOLD = const(0x2201)
_SI4713_PROP_TX_ACOMP_ENABLE = const(0x2200)
_SI4713_PROP_TX_AUDIO_DEVIATION = const(0x2101)
_SI4710_CMD_POWER_DOWN = const(0x11)
_SI4713_PROP_TX_PREEMPHASIS = const(0x2106)

_SI4713_PROP_TX_ATTACK_TIME = const(0x2202)
_SI4713_PROP_TX_RELEASE_TIME = const(0x2203)

OnAirled = digitalio.DigitalInOut(board.GP8)
Lockedled = digitalio.DigitalInOut(board.GP9)
Clipled = digitalio.DigitalInOut(board.GP10)
Failureled = digitalio.DigitalInOut(board.GP11)
Initled = digitalio.DigitalInOut(board.GP16)
Overloaddled = digitalio.DigitalInOut(board.GP15)
Limitled = digitalio.DigitalInOut(board.GP14)

OnAirled.direction = digitalio.Direction.OUTPUT
Lockedled.direction = digitalio.Direction.OUTPUT
Clipled.direction = digitalio.Direction.OUTPUT
Failureled.direction = digitalio.Direction.OUTPUT
Initled.direction = digitalio.Direction.OUTPUT
Overloaddled.direction = digitalio.Direction.OUTPUT
Limitled.direction = digitalio.Direction.OUTPUT

Initled.value = True

message_started = False

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
    esp8266 = busio.UART(board.GP12, board.GP13, baudrate=11520)
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
    display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
    display = adafruit_displayio_sh1106.SH1106(display_bus, width=128, height=32)
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
    si4713 = adafruit_si4713.SI4713(i2c, reset=si_reset, timeout_s=5)
    print("[system] initialized si4713 instance")
    simpleio.tone(board.GP4, 1000, duration=0.1)
except Exception as e:
    simpleio.tone(board.GP4, 440, duration=0.1)
    print("[system] initializing si4713 failed")
    print(e)
    time.sleep(1)
    #microcontroller.reset()

"""
WIDTH = 128
HEIGHT = 32  # Change to 64 if needed
BORDER = 5
    
# Make the display context
splash = displayio.Group()
display.show(splash)

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(WIDTH - BORDER * 2, HEIGHT - BORDER * 2, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x000000  # Black
inner_sprite = displayio.TileGrid(
    inner_bitmap, pixel_shader=inner_palette, x=BORDER, y=BORDER
)
splash.append(inner_sprite)

# Draw a label
text = "Hello World!"
text_area = label.Label(
    terminalio.FONT, text=text, color=0xFFFFFF, x=28, y=HEIGHT // 2 - 1
)
splash.append(text_area)
"""

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
    
display.clear()
display.print(f"Please wait...")
"""

def pad_with_zeros(number, width):
    padded_number = "0" * (width - len(str(number))) + str(number)
    return padded_number

class Settings:
    def __init__(self):
        # more info https://en.wikipedia.org/wiki/Radio_Data_System
        # general
        self.statuscheck = False
        self.stereo = True
        self.power = 115
        self.frequency_khz = 107500 # Khz
        self.PreEmphasis = "50"
        # limiter
        # enable this if you not use audio processor
        self.compressed = 0xFFF6 # hex 10000 - DEC 0 - 40 off 0x0000
        self.ACEN = True # Warning: this mode is Over mod if not compressed
        # RDS
        self.RDS = True
        self.RDSpicode = 0x27C8
        self.RDSps = b"HSA62BFM"
        self.RDSrt = b""
        self.RDSpty = 9
        self.RDSdynamicpty = True
        self.RDStp = False
        self.RDSartificialhead = False
        self.RDSforceb = True
        self.RDSta = False
        self.RDSms = True
        self.RDSaf = 99.30 # Mhz
        # other
        self.FastStartup = False
        self.PLLchecksec = 5
        self.Audiodeviation = 68.5 #Khz
        
        # settings value
        self.prestereo = None
        self.preRDS = None
        self.restarted = None

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
    
    def updateRDSaf(self):
        if self.RDSaf < 87.6 or self.RDSaf > 107.9:
            print("[SI4713 RDS] Frequency out of range. Supported range: 87.6 MHz to 107.9 MHz")
            si4713.setProperty(_SI4713_PROP_TX_RDS_PS_AF, 0xE0E0)
            return
        
        af_value = int((self.RDSaf - 87.6) * 10) + 0xE100
       
        si4713.setProperty(_SI4713_PROP_TX_RDS_PS_AF, af_value)
    
    def updateDeviation(self):
        audio_deviation_units = int(self.Audiodeviation * 100)
        property_value = audio_deviation_units & 0xFFFF
        si4713.setProperty(_SI4713_PROP_TX_AUDIO_DEVIATION, property_value)
        
    def StereoRDSswitch(self):
        time.sleep(0.1)
        if self.stereo is False and self.RDS:
            si4713.setProperty(_SI4713_PROP_TX_COMPONENT_ENABLE, 0x04)  # mono and RDS
        elif self.stereo and self.RDS:
            si4713.setProperty(_SI4713_PROP_TX_COMPONENT_ENABLE, 0x07)  # stereo and RDS
        elif self.stereo is False and self.RDS is False:
            si4713.setProperty(_SI4713_PROP_TX_COMPONENT_ENABLE, 0x00)  # mono only
        elif self.RDS is False:
            si4713.setProperty(_SI4713_PROP_TX_COMPONENT_ENABLE, 0x03)  # stereo only

    def updateRDSmisc(self):
        if self.compressed == 0x0000:
            RDScompressed = False
        else:
            RDScompressed = True
        hex = self._RDSmiscgen(self.stereo, self.RDSartificialhead, RDScompressed, self.RDSdynamicpty,
                                            self.RDStp, self.RDSpty, self.RDSforceb, self.RDSta, self.RDSms)
        si4713.setProperty(_SI4713_PROP_TX_RDS_PS_MISC, hex)

    def SInit(self):
        si4713.reset()
        noise = si4713.received_noise_level(settings.frequency_khz)
        print("[SI4713] Noise at {0:0.3f} mhz: {1} dBuV".format(self.frequency_khz / 1000.0, noise))
        
        if self.restarted is not None:
            self.stereo = self.prestereo
            self.RDS = self.preRDS
        
        """
        if not self.FastStartup:
            display.clear()
            display.print(f"Freq {self.frequency_khz / 1000.0} Mhz\nPower {self.power} dBuV")
            time.sleep(1)
        """
        
        si4713.tx_frequency_khz = self.frequency_khz
        si4713.tx_power = 88
        si4713.setProperty(_SI4713_PROP_TX_COMPONENT_ENABLE, 0x00)  # mono only
        
        si4713.setProperty(_SI4713_PROP_TX_LINE_INPUT_MUTE, 0x03)
        si4713.setProperty(_SI4713_PROP_TX_ACOMP_THRESHOLD, self.compressed)
        if self.compressed == 0x0000:
            limiter = False
        else:
            limiter = True
            
        if limiter and self.ACEN:
            si4713.setProperty(_SI4713_PROP_TX_ACOMP_ENABLE, 0x0003)
        elif limiter and not self.ACEN:
            si4713.setProperty(_SI4713_PROP_TX_ACOMP_ENABLE, 0x0002)
        elif not limiter and self.ACEN:
            si4713.setProperty(_SI4713_PROP_TX_ACOMP_ENABLE, 0x0001)
        elif not limiter and not self.ACEN:
            si4713.setProperty(_SI4713_PROP_TX_ACOMP_ENABLE, 0x0000)
            
        if self.PreEmphasis == "75":
            si4713.setProperty(_SI4713_PROP_TX_PREEMPHASIS, 0x0000)
        elif self.PreEmphasis == "50":
            si4713.setProperty(_SI4713_PROP_TX_PREEMPHASIS, 0x0001)
        elif self.PreEmphasis == "off":
            si4713.setProperty(_SI4713_PROP_TX_PREEMPHASIS, 0x0002)
        
        
        """
        if not self.FastStartup:
            display.clear()
            display.print(f"Limiter {'On' if limiter else 'off'}\nACEN {'On' if self.ACEN else 'off'}")
            time.sleep(1)
        """

        if self.RDS:
            si4713.configure_rds(self.RDSpicode, station=self.RDSps, rds_buffer=self.RDSrt)
            self.updateRDSmisc()
            time.sleep(0.1)
            self.updateRDSaf()
        
        self.StereoRDSswitch()
        """
        if not self.FastStartup:
            display.clear()
            display.print(f"Stereo {'On' if self.stereo else 'off'}\nRDS {'On' if self.RDS else 'off'}")
            time.sleep(1)
        """
        
        self.updateDeviation()
        
        
        for option, value in self.getData():
            esp8266.write(bytes(f"{option} {value}\n", 'utf-8'))
            time.sleep(0.1)

        print("[SI4713] Transmitting at {0:0.3f} mhz".format(self.frequency_khz / 1000.0))
        print("[SI4713] Transmitter power: {0} dBuV".format(self.power))
        print("[SI4713] Transmitter antenna capacitance: {0:0.2} pF".format(si4713.tx_antenna_capacitance))

        print("[SI4713] Broadcasting...")

        esp8266.write(bytes(f"txfreq {self.frequency_khz / 1000.0}\n", 'utf-8'))
        esp8266.write(bytes(f"txpower {self.power}\n", 'utf-8'))
        esp8266.write(bytes(f"txantennacap {si4713.tx_antenna_capacitance}\n", 'utf-8'))

        # display.clear()
        # display.print(f"Broadcasting...\nOn Air on {FREQUENCY_KHZ/1000}")

        OnAirled.value = True
        Initled.value = False
        """
        display.clear()
        display.print(f"Broadcasting on\n{self.frequency_khz / 1000.0} Mhz")
        """
        if not self.FastStartup:
            time.sleep(1)
            self.waitlock()
            time.sleep(1)
        else:
            print("[SI4713] PLL locked!")
            Lockedled.value = True
            si4713.setProperty(_SI4713_PROP_TX_LINE_INPUT_MUTE, 0x00)
            si4713.tx_power = self.power
        """
        display.clear()
        display.print(f"Broadcasting...\nlocked")
        """
    
    def powerdown(self):
        print("[SI4713] Shutdown...")
        #_buffer = bytearray(10)
        """
        display.clear()
        display.print(f"Shutdown...")
        """
        time.sleep(1)
        Lockedled.value = False
        self.prestereo = self.stereo
        self.preRDS = self.RDS
        self.restarted = True
        self.stereo = False
        self.RDS = False
        self.StereoRDSswitch()
        time.sleep(1)
        si4713.tx_power = 88
        time.sleep(1)
        si4713.setProperty(_SI4713_PROP_TX_LINE_INPUT_MUTE, 0x03)
        time.sleep(1)
        OnAirled.value = False
        si4713.reset()
        time.sleep(1)
        """
        display.clear()
        display.print("FM Transmitter\nV1.0")
        """
        
    def waitlock(self):
        for i in reversed(range(self.PLLchecksec)):
            """
            display.clear()
            display.print(f"Broadcasting...\nwait lock in {i}")
            """
            time.sleep(1)

        print("[SI4713] PLL locked!")
        Lockedled.value = True
        si4713.setProperty(_SI4713_PROP_TX_LINE_INPUT_MUTE, 0x00)
        si4713.tx_power = self.power
        

settings = Settings()

try:
    settings.SInit()
except Exception as e:
    Failureled.value = True
    simpleio.tone(board.GP4, 440, duration=0.1)
    print(e)

time.sleep(0.1)
esp8266.reset_input_buffer()

while True:
    try:
        while True:
            if esp8266.in_waiting > 0:
                try:
                    data = esp8266.read(200).decode("utf-8")
                    
                    print("[Serial] " + data)
                        
                    data = data.split("|")[0]
                
                    print("[Command] " + data)

                    try:
                        if data.startswith("setrdsbuffer "):
                            si4713.rds_buffer = bytes(data.split("setrdsbuffer ")[1].replace("+", " "), "utf-8")
                        elif data.startswith("setrdstation "):
                            si4713.rds_station = bytes(data.split("setrdstation ")[1], "utf-8")
                        elif data.startswith("setgentxpower "):
                            si4713.tx_power = int(data.split("setgentxpower ")[1])
                        elif data.startswith("settxfreq "):
                            si4713.tx_frequency_khz = int(data.split("settxfreq ")[1])
                        elif data.startswith("getdata"):
                            for option, value in settings.getData():
                                esp8266.write(bytes(f"{option} {value}\n", 'utf-8'))
                                time.sleep(0.1)
                        elif data.startswith("setrdspty "):
                            settings.RDSpty = int(data.split("setrdspty ")[1])
                            settings.updateRDSmisc()
                        elif data.startswith("setaudiochannel "):
                            data = data.split("setaudiochannel ")[1]
                            if data == "mono":
                                settings.stereo = False
                            elif data == "stereo":
                                settings.stereo = True
                            settings.updateRDSmisc()
                            settings.StereoRDSswitch()
                        elif data.startswith("setrds "):
                            data = data.split("setrds ")[1]
                            if data == "enable":
                                settings.RDS = True
                            elif data == "disable":
                                settings.RDS = False
                            settings.StereoRDSswitch()
                        elif data.startswith("powerup"):
                            settings.SInit()
                        elif data.startswith("powerdown"):
                            settings.powerdown()
                            #break
        

                    except Exception as e:
                        print(e)
    
                        
                    #esp8266.reset_input_buffer()
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(e)
                    
            if settings.statuscheck:
                input_level = si4713.input_level
                audio_signal_status = si4713.audio_signal_status
                # print("[SI4713] Input level: {0} dBfs".format(input_level))
                # print("[SI4713] ASQ status: 0x{0:02x}".format(audio_signal_status))
                # print(f"[ADS1115] audio L: {audioL.voltage} | AudioR: {audioR.voltage}")
                esp8266.write(bytes(f"INLE {input_level}\n", 'utf-8'))
                esp8266.write(bytes(f"ASQ {audio_signal_status}\n", 'utf-8'))
                #esp8266.write(bytes(f"AudioL {audioL.voltage}\n", 'utf-8'))
                #esp8266.write(bytes(f"AudioR {audioR.voltage}\n", 'utf-8'))
            

                # display.clear()
                # display.print(f"Input level: {input_level} dBfs")
                
                if audio_signal_status == 0x05:
                    print("[SI4713] Limit!!")
                    #esp8266.write(bytes(f"ASQW Limit\n", 'utf-8'))
                    Limitled.value = True
                else:
                    Limitled.value = False

                if input_level == 0 and audio_signal_status == 0x04:
                    print("[SI4713] OverMod!!")
                    #esp8266.write(bytes(f"ASQW OverMod\n", 'utf-8'))
                    Overloaddled.value = True
                else:
                    Overloaddled.value = False

                if input_level == 0 and audio_signal_status == 0x00:
                    print("[SI4713] Clip!!")
                    #esp8266.write(bytes(f"ASQW Clip\n", 'utf-8'))
                    Clipled.value = True
                else:
                    Clipled.value = False

            time.sleep(0.1)
            
            #esp8266.reset_input_buffer()

    except Exception as e:
        Failureled.value = True
        simpleio.tone(board.GP4, 440, duration=0.1)
        print(e)
        if str(e) == "[Errno 19] No such device":
            print("[System] Try restart SI4713")
            OnAirled.value = False
            Lockedled.value = False
            time.sleep(1)
            settings.SInit()
            settings.waitlock()
            """
            display.clear()
            display.print(f"Broadcasting...\nlocked")
            """
            Failureled.value = False

# wait for button press 

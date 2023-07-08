import board
import digitalio
import busio
import adafruit_si4713
import simpleio
import time
import i2c_pcf8574_interface
# import si4713_addons
import lcd
import rotaryio


print("[system] initializing i2c")
try:
    i2c = busio.I2C(board.GP7, board.GP6)
    print("[system] initialized i2c")
except Exception as e:
    print("[system] initializing i2c failed")
    print(e)
    time.sleep(1)
    
print("[system] initializing lcd")
try:
    i2clcd = i2c_pcf8574_interface.I2CPCF8574Interface(i2c, 0x27)
    display = lcd.LCD(i2clcd, num_rows=2, num_cols=16)
    display.set_backlight(True)
    display.set_display_enabled(True)
    print("[system] initialized lcd")
except Exception as e:
    print("[system] initializing lcd failed")
    print(e)
    time.sleep(1)
    
sw_pin = digitalio.DigitalInOut(board.GP28)
sw_pin.direction = digitalio.Direction.INPUT
sw_pin.pull = digitalio.Pull.UP

display.clear()
display.print("Main")

encoder = rotaryio.IncrementalEncoder(board.GP26, board.GP27)

Settings_page = 0

def center_string(text, length):
    if len(text) >= length:
        return text
    else:
        spaces = length - len(text)
        left_spaces = spaces // 2
        right_spaces = spaces - left_spaces
        centered_text = ' ' * left_spaces + text + ' ' * right_spaces
        return centered_text

settingsMenu = False

def settingspage():
    global settingsMenu
    last_position = None
    
    aboutmenu = False
    RDSmenu = False

    while settingsMenu:
        position = encoder.position
        if last_position is None or position != last_position:
            print(position)
            if position == 0:
                message = f"Tx Frequency"
            elif position == 1:
                message = f"Tx Power"
            elif position == 2:
                message = f"Audio Channel"
            elif position == 3:
                message = f"Audio Level"
            elif position == 4:
                message = f"RDS"
            elif position == 5:
                message = f"Network"
            elif position == 9:
                message = f"About"
            elif position == 10:
                message = f"Exit"
            else:
                message = str(position)

                
            display.clear()
            display.print(f"{center_string('Settings', 16)}\n{position}\n{center_string(message, 16)}")
            
        if not sw_pin.value:
            if position == 9:
                RDSmenu = True
                settingsMenu = False
                display.clear()
                display.print("Firmware 1.0\nTransmitter 1.0")
            elif position == 10:
                settingsMenu = False
                display.clear()
                display.print("Main")
            
        last_position = position
            
        time.sleep(0.1)
    
    while RDSmenu:

        

while True:
    if not sw_pin.value:
        settingsMenu = True
        settingspage()
    
    
           
        
    

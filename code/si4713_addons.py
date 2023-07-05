import busio
import adafruit_si4713
import digitalio

SI4713_I2C_ADDR = 0x63

class si4713Addons:
    def __init__(self, I2C, adaSI4713):
        self.adasi4713 = adaSI4713
        self.I2C = I2C
        
        #self.si_reset.direction = Direction.OUTPUT
        
        
        while not i2c.try_lock():
            pass
        
        
    def powerup(self):
        si4713.tx_frequency_khz = si4713.tx_frequency_khz
        si4713.tx_power = si4713.tx_power
        
    def powerdown(self):
        self.I2C.writeto(SI4713_I2C_ADDR, bytearray([0x11]))

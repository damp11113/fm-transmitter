import busio
import digitalio

SI4713_I2C_ADDR = 0x63

class SI4713:
    def __init__(self, i2c, reset):
        self.i2c = i2c
        self.reset = reset
        
        self.reset.switch_to_output(value=True)
        
        while not self.i2c.try_lock():
            pass
        
    
    def powerup(self, analog_audio_inputs = True):
        self._assert_reset()
        self.i2c.writeto(SI4713_I2C_ADDR, bytearray([0x01, 0x12, 0x50 if analog_audio_inputs else 0x0F]))
        time.sleep(0.2)
        
    
    def powerdown(self):
        self.i2c.writeto(SI4713_I2C_ADDR, bytearray([0x11]))
    
    def _assertreset(self):
        self.reset.value = True
        time.sleep(0.01)
        self.reset.value = False
        time.sleep(0.01)
        self.reset.value = True
        time.sleep(0.25)

     def set_frequency(self, freq):
        assert self.FREQ_MIN <= freq <= self.FREQ_MAX
        assert (freq // 1e3) % 50 == 0

        self._frequency = freq
        freq = round(freq // self.FREQ_UNIT)
        self._write_bytes(array('B', [0x30, 0x00, freq >> 8 & 0xFF, freq & 0xFF]))
        time.sleep(0.2)  # need 100ms
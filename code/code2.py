import time
import array
import math
import audiocore
import board
import audiobusio

audio = audiobusio.I2SOut(board.GP0, board.GP1, board.GP2)

def gentone(freq, tone_volume=0.1):
    length = 8000 // freq
    sine_wave = array.array("h", [0] * length)
    for i in range(length):
        sine_wave[i] = int((math.sin(math.pi * 2 * i / length)) * tone_volume * (2 ** 15 - 1))
    return audiocore.RawSample(sine_wave)


while True:
    for i in range(1, 8000, 10):
        print(i)
        audio.play(gentone(i, 0.5), loop=True)
        time.sleep(0.1)
        audio.stop()
    time.sleep(1)

# By Prof. John Gallaugher as a demo of fun things you can do with the 
# Adafruit Circuit Playground Bluefruit
# for more projects, see: https://YouTube.com/profgallaugher
# Twitter: @gallaugher, or gallaugher.com
# an old video of build at: http://bit.ly/cpxb-halloween-head-video
# but the code below has been updated for CircuitPython 7.0
# I'll try to get a new build video up at some point.
#
# Sound files are on YouTube. Put them in your CPB in a folder
# named sounds. Sound files are: 
# hey.wav
# hey_you.wav
# take_candy.wav
# theres_candy_in_my_head.wav
# open_my_head.wav
# ah_dont_take_candy_from_strangers.wav

import board
import neopixel
import digitalio
import analogio
import simpleio
import busio
import touchio
import time
from digitalio import DigitalInOut, Direction, Pull
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.color_packet import ColorPacket
from adafruit_bluefruit_connect.button_packet import ButtonPacket
# import lines needed to play sound files
from audiopwmio import PWMAudioOut as AudioOut
from audiocore import WaveFile

# set up touchpads A1
touchpad_A1 = touchio.TouchIn(board.A1)

# setup pixels
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.3, auto_write=True)

# name colors so you don't need to refer to numbers
RED = (255, 0, 0)
ORANGE = (255, 50, 0)
BLACK = (0, 0, 0)

# setup bluetooth
ble = BLERadio()
uart_server = UARTService()
advertisement = ProvideServicesAdvertisement(uart_server)
# Give your CPB a unique name between the quotes below
advertisement.complete_name = "skull"

# set up the speaker
speaker = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
speaker.direction = digitalio.Direction.OUTPUT
speaker.value = True
audio = AudioOut(board.SPEAKER)

# set path where sound files can be found
path = "sounds/"

def play_sound(filename):
    with open(path + filename, "rb") as wave_file:
        wave = WaveFile(wave_file)
        audio.play(wave)
        while audio.playing:
            pass

def checkTouch():
    # check if touched. If so, play sound
    if touchpad_A1.value:
        print("Touched!")
        pixels.fill(ORANGE)
        play_sound("ah_dont_take_candy_from_strangers.wav")
        pixels.fill(BLACK)

while True:
    ble.start_advertising(advertisement)
    while not ble.connected:
        checkTouch()

    # Now we're connected so we don't need to advertise the device as one that you're able to connect to
    ble.stop_advertising()
    
    # Now we're connected

    while ble.connected:
        # check if touched. If so, play sound
        checkTouch()
            
        if uart_server.in_waiting:
            try:
                packet = Packet.from_stream(uart_server)
            except ValueError:
                continue # or pass. This will start the next

            if isinstance(packet, ColorPacket): # check if a color was sent from color picker
                pixels.fill(packet.color)
            if isinstance(packet, ButtonPacket): # check if a button was pressed from control pad
                if packet.pressed:
                    if packet.button == ButtonPacket.BUTTON_1: # if button #1
                        pixels.fill(RED)
                        play_sound("hey.wav")
                        pixels.fill(BLACK)
                    if packet.button == ButtonPacket.BUTTON_2: # if button #2
                        pixels.fill(ORANGE)
                        play_sound("hey_you.wav")
                        pixels.fill(BLACK)
                    if packet.button == ButtonPacket.BUTTON_3: # if button #2
                        pixels.fill(RED)
                        play_sound("take_candy.wav")
                        pixels.fill(BLACK)
                    if packet.button == ButtonPacket.BUTTON_4: # if button #2
                        pixels.fill(ORANGE)
                        play_sound("theres_candy_in_my_head.wav")
                        pixels.fill(BLACK)
                    if packet.button == ButtonPacket.UP: # if button #2
                        pixels.fill(RED)
                        play_sound("open_my_head.wav")
                        pixels.fill(BLACK)

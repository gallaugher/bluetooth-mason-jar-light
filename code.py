# bluetooth-mason-jar-light.py
# By John Gallaugher https://gallaugher.com  BlueSky: @gallaugher.bsky.social
# YouTube: https://YouTube.com/@BuildWithProfG
# Step-by-step build video in playlist at: https://bit.ly/circuitpython-school

# Run into build trouble? Adafruit runs a great help forum at:
# https://forums.adafruit.com - most questions are answered within an hour.
# Adafruit also has a discord channel at:
# http://adafru.it/discord

import board, neopixel, time

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.color_packet import ColorPacket
from adafruit_bluefruit_connect.button_packet import ButtonPacket

# import animations and colors
# While we don't use all of these animations and colors
# I import them all below in case you want to experiment with them.
# Full documentation for the adafruit_led_animation library is at:
# https://circuitpython.readthedocs.io/projects/led-animation/en/latest/api.html

from adafruit_led_animation.animation.solid import Solid
from adafruit_led_animation.animation.colorcycle import ColorCycle
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.rainbowChase import RainbowChase
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.animation.SparklePulse import SparklePulse
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation.color import RED, YELLOW, ORANGE, GREEN, TEAL, CYAN, BLUE, \
    PURPLE, MAGENTA, GOLD, PINK, AQUA, JADE, AMBER, OLD_LACE, WHITE, BLACK, RAINBOW

# setup bluetooth
ble = BLERadio()
uart_server = UARTService()
advertisement = ProvideServicesAdvertisement(uart_server)
# Give your CPB a unique name between the quotes below
advertisement.complete_name = "JarLight"
ble.name = advertisement.complete_name  # This should make it show in the Bluefruit Connect app. It often takes time to show.
print(f"ble.name is {ble.name}")

runAnimation = False # is an animation running?
animation_number = -1 # no initial animation set
current_animation = None
light_position = -1 # used for up/down arrows. No position set yet

# Update to match the pin connected to your NeoPixels if you are using a different pad/pin.
led_pin = board.A1
# UPDATE NUMBER BELOW to match the number of NeoPixels you have connected
num_leds = 20
defaultColor = AMBER
pickedColor = defaultColor

defaultTime = 0.1
minWaitTime = 0.01
hundredths = 0.01
tenths = 0.1
adjustedTime = defaultTime

strip = neopixel.NeoPixel(led_pin, num_leds, brightness=0.85, auto_write=False)

# for night-rider, battlestar galactica larson scanner effect, set length to something like 3 and speed to a bit longer like 0.2
# Comet has a dimming tale and can also bounce back.
cometTailLength = int(num_leds / 3) + 1
strip.fill(pickedColor)
strip.show() # We initially light up all pixels in the default color.
first_time = True

def configureRainbowAnimation():
    global first_time
    global current_animation
    print(f"adjustedTime: {adjustedTime}, pickedColor: {pickedColor}")
    # Rainbow: Entire strip starts RED and all lights fade together through rainbow
    rainbowAnimation = Rainbow(strip, speed=adjustedTime, period=2)
    # RainbowSparkle: Strip sparkes all one color (Red first), then sparkles all one color through rest of the rainbow
    rainbowSparkleAnimation = RainbowSparkle(strip, speed=adjustedTime, period=5, num_sparkles=int(num_leds / 3))
    # RainbowComet - is a larson-style chase effect with comet in a rainbow pattern.
    rainbowCometAnimation = RainbowComet(strip, speed=adjustedTime, tail_length=cometTailLength, bounce=True)
    # the animation below runs all three animations, one after the other.
    return AnimationSequence(rainbowAnimation, rainbowCometAnimation,
                                        rainbowSparkleAnimation, advance_interval=5, auto_clear=True)

# The function runSelected will run the animation number stored in the value animation_number.
# This function is called in the while True: loop whenever an animation has been started, in while not ble.connected (when not connected to bluetooth)
# or while ble.connected (when connected to bluetooth). We call it in both locations so that if
# animations are started, then the user shuts off their phone or moves out of bluetooth range, the
# last selected animation will continue to run.
def runSelectedAnimation():
    global first_time
    global current_animation
    if first_time:
        strip.fill(BLACK)
        strip.show()
    if animation_number == 1:
        if first_time:
            print("*** COMET or LARSON SCANNER ***")
            # I set bounce = False because that makes it look circular.
            # for a tie it's better to True so it looks like it bounces up and down.
            print(f"adjustedTime: {adjustedTime}, pickedColor: {pickedColor}")
            current_animation = Comet(strip, speed=adjustedTime, color=pickedColor, tail_length=cometTailLength, bounce=False)
            first_time = False
        current_animation.animate()
    elif animation_number == 2:
        if first_time:
            print("*** PULSE ***")
            print(f"adjustedTime: {adjustedTime}, pickedColor: {pickedColor}")
            current_animation = Pulse(strip, speed=adjustedTime, color=pickedColor, period=3)
            first_time = False
        current_animation.animate()
    elif animation_number == 3:
        if first_time:
            print("*** SPARKLE PULSE ***")
            print(f"adjustedTime: {adjustedTime}, pickedColor: {pickedColor}")
            current_animation = SparklePulse(strip, speed=adjustedTime, period=12, color=pickedColor)
            first_time = False
        current_animation.animate()
    elif animation_number == 4:
        if first_time:
            rainbowSequence = configureRainbowAnimation()
            print("*** RAINBOW ***")
            current_animation = rainbowSequence
            first_time = False
        current_animation.animate()

times_packet_checked = 0
print("Bluetooth Mason Jar Code is Running!")
while True:
    ble.start_advertising(advertisement)
    while not ble.connected:
        if runAnimation:
            runSelectedAnimation()

    # Now that we're connected we no longer need to advertise the CPB as available for connection.
    ble.stop_advertising()

    while ble.connected:
        if uart_server.in_waiting:
            try:
                packet = Packet.from_stream(uart_server)
            except ValueError:
                continue  # or pass. This will start the next

            if isinstance(packet, ColorPacket):  # A color was selected from the app color picker
                print("*** color sent")
                print("pickedColor = ", ColorPacket)
                runAnimation = False
                animation_number = 0
                strip.fill(packet.color)  # fills strip in with the color sent from Bluefruit Connect app
                strip.show()
                pickedColor = packet.color
                # reset light_position after picking a color
                light_position = -1

            times_packet_checked += 1
            print(f"Checking Packet: {times_packet_checked}")
            if isinstance(packet, ButtonPacket):  # A button was pressed from the app Control Pad
                if packet.pressed:
                    if packet.button == ButtonPacket.BUTTON_1:  # app button 1 pressed
                        first_time = True
                        animation_number = 1
                        runAnimation = True
                    elif packet.button == ButtonPacket.BUTTON_2:  # app button 2 pressed
                        first_time = True
                        animation_number = 2
                        runAnimation = True
                    elif packet.button == ButtonPacket.BUTTON_3:  # app button 3 pressed
                        first_time = True
                        animation_number = 3
                        runAnimation = True
                    elif packet.button == ButtonPacket.BUTTON_4:  # app button 4 pressed
                        first_time = True
                        animation_number = 4
                        runAnimation = True
                    elif packet.button == ButtonPacket.UP or packet.button == ButtonPacket.DOWN:
                        # if up or down was pressed, stop animation and move a single light
                        # up or down on the strand each time the up or down arrow is pressed.
                        animation_number = 0
                        runAnimation = False
                        # The UP or DOWN button was pressed.
                        increase_or_decrease = 1
                        if packet.button == ButtonPacket.DOWN:
                            increase_or_decrease = -1
                        light_position += increase_or_decrease
                        if light_position >= len(strip):
                            light_position = len(strip) - 1
                        if light_position <= -1:
                            light_position = 0
                        strip.fill([0, 0, 0])
                        print(f"pickedColor: {pickedColor}")
                        strip[light_position] = pickedColor
                        strip.show()
                    elif packet.button == ButtonPacket.RIGHT:  # right button will speed up animations
                        # The RIGHT button was pressed.
                        first_time = True
                        runAnimation = True
                        # reset light_position after animation
                        light_position = -1
                        if adjustedTime <= 0.1:
                            adjustedTime = adjustedTime - hundredths
                        else:
                            adjustedTime = adjustedTime - tenths
                        if adjustedTime <= 0.0:
                            adjustedTime = minWaitTime
                        print(f"adjustedTime: {adjustedTime}")
                    elif packet.button == ButtonPacket.LEFT:  # left button will slow down animations
                        # The LEFT button was pressed.
                        first_time = True
                        runAnimation = True
                        # reset light_position after animation
                        light_position = -1
                        if adjustedTime >= 0.1:
                            adjustedTime = adjustedTime + tenths
                        else:
                            adjustedTime = adjustedTime + hundredths
                        print(f"adjustedTime: {adjustedTime}")
        if runAnimation == True:
            runSelectedAnimation()
    # If we got here, we lost the connection. Go up to the top and start
    # advertising again and waiting for a connection.

# Write your code here :-)
import time
import analogio
import busio as io
import board
import displayio
import neopixel
import adafruit_ht16k33.segments
import adafruit_il0373

## Hardware Configuration
FSR = analogio.AnalogIn(board.A3)
NPIN = board.NEOPIXEL
num_pixels = 1
pixels = neopixel.NeoPixel(NPIN, num_pixels, brightness=.01 , auto_write=False)
i2c = io.I2C(board.SCL, board.SDA)

# Lock the I2C device before we try to scan
while not i2c.try_lock():
    pass
# Print the addresses found once
print("I2C addresses found:", [hex(device_address)
                               for device_address in i2c.scan()])

# Unlock I2C now that we're done scanning.
i2c.unlock()

print("i2c complete")
display = adafruit_ht16k33.segments.Seg14x4(i2c, address=0x70)


'''# Set based on your display
FLEXIBLE = False
TRICOLOR = True
ROTATION = 90

# Used to ensure the display is free in CircuitPython
displayio.release_displays()

# Define the pins needed for display use
# This pinout is for a Feather M4 and may be different for other boards
# For the Metro/Shield, esc is board.D10 and dc is board.D9
spi = board.SPI()  # Uses SCK and MOSI
ecs = board.D9
dc = board.D10
rst = board.D5    # set to None for FeatherWing/Shield
busy = board.D6   # set to None for FeatherWing/Shield

if TRICOLOR:
    highlight = 0xff0000 #third color is red (0xff0000)
else:
    highlight = 0x000000

# Create the displayio connection to the display pins
display_bus = displayio.FourWire(spi, command=dc, chip_select=ecs,
                                 reset=rst, baudrate=1000000)

time.sleep(1)  # Wait a bit

# Create the display object

display = adafruit_il0373.IL0373(display_bus, width=212, height=104, swap_rams=FLEXIBLE, # 2.13" Tri-color
                                 busy_pin=busy, rotation=ROTATION,
                                 highlight_color=highlight)

# Create a display group for our screen objects
g = displayio.Group()

# Display a ruler graphic from the root directory of the CIRCUITPY drive
f = open("/5BDL-w212.bmp", "rb")

pic = displayio.OnDiskBitmap(f)
# Create a Tilegrid with the bitmap and put in the displayio group
t = displayio.TileGrid(pic, pixel_shader=displayio.ColorConverter())
g.append(t)

# Place the display group on the screen
display.show(g)

# Refresh the display to have it actually show the image
# NOTE: Do not refresh eInk displays sooner than 180 seconds
display.refresh()
print("refreshed")
'''

## Software Configuration
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

## Function Definition
def get_voltage(pin):
    return (pin.value * 3.3) / 65536

## Main Loop
while True:
    FSR_value = (get_voltage(FSR))
    print("A1 Voltage reading is", (get_voltage(FSR)))
    time.sleep(0.5)
    dFSR = round(FSR_value, 3)
    display.print(dFSR)
    time.sleep(0.2)

    if (FSR_value > 2.1):
        print("Value is Green")
        pixels.fill(GREEN)
        pixels.show()
    if (FSR_value < 2.09):
        print("Value is RED")
        pixels.fill(BLUE)
        pixels.show()
        time.sleep(0.5)
        pixels.fill(RED)
        pixels.show()

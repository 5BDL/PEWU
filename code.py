# Write your code here :-)
import time
import analogio
import digitalio
import busio as io
import board
import displayio
import neopixel
import adafruit_ht16k33.segments
from adafruit_esp32spi import adafruit_esp32spi
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_requests as requests

## Hardware Configuration
WaterFSR = analogio.AnalogIn(board.A3)
FoodFSR = analogio.AnalogIn(board.A2)
NPIN = board.NEOPIXEL
num_pixels = 1
TESTMODE = 0

#pixels = neopixel.NeoPixel(NPIN, num_pixels, brightness=.01 , auto_write=False)

# Wifi
esp32_cs = digitalio.DigitalInOut(board.D13)
esp32_ready = digitalio.DigitalInOut(board.D11)
esp32_reset = digitalio.DigitalInOut(board.D12)

spi = io.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

'''# -------
if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")
print("Firmware vers.", esp.firmware_version)
print("MAC addr:", [hex(i) for i in esp.MAC_address])

for ap in esp.scan_networks():
    print("\t%s\t\tRSSI: %d" % (str(ap['ssid'], 'utf-8'), ap['rssi']))

TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
JSON_URL = "http://api.coindesk.com/v1/bpi/currentprice/USD.json"
requests.set_socket(socket, esp)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")
print("Firmware vers.", esp.firmware_version)
print("MAC addr:", [hex(i) for i in esp.MAC_address])

for ap in esp.scan_networks():
    print("\t%s\t\tRSSI: %d" % (str(ap['ssid'], 'utf-8'), ap['rssi']))

print("Connecting to AP...")
while not esp.is_connected:
    try:
        esp.connect_AP(b'Berkshire', b'Berkshire123')
    except RuntimeError as e:
        print("could not connect to AP, retrying: ",e)
        continue
print("Connected to", str(esp.ssid, 'utf-8'), "\tRSSI:", esp.rssi)
print("My IP address is", esp.pretty_ip(esp.ip_address))
print("IP lookup adafruit.com: %s" % esp.pretty_ip(esp.get_host_by_name("adafruit.com")))
print("Ping google.com: %d ms" % esp.ping("google.com"))

#esp._debug = True
print("Fetching text from", TEXT_URL)
r = requests.get(TEXT_URL)
print('-'*40)
print(r.text)
print('-'*40)
r.close()

print()
print("Fetching json from", JSON_URL)
r = requests.get(JSON_URL)
print('-'*40)
print(r.json())
print('-'*40)
r.close()

print("Done!")
'''

# TESTMODE for Threshold -----

if TESTMODE == 1:
    i2c = io.I2C(board.SCL, board.SDA)

    while not i2c.try_lock():
        pass
    print("I2C addresses found:", [hex(device_address)
                                for device_address in i2c.scan()])
    i2c.unlock()
    print("i2c complete")
    display = adafruit_ht16k33.segments.Seg14x4(i2c, address=0x70)

# END TESTMODE -----

## Software Configuration
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
waterThreshold = 2.20
foodThreshold = 2.01
checkTime = 3600

## Function Definition
def get_voltage(pin):
    return (pin.value * 3.3) / 65536

## NOTES
'''
11/30/19 - Testing
Empty Bowl = 2.27
Halfway Full Water = 2.625
Quarter Full Food = 2.59
Assume Empty Bowl @ 2.35
'''

## Main Loop
while True:
    Water_value = (get_voltage(WaterFSR))
    print("A3 Voltage reading is", Water_value)
    Food_value = (get_voltage(FoodFSR))
    print("A2 Voltage reading is", Food_value)
    dwater = round(Water_value, 3)
    dfood = round(Food_value, 3)
    s_dwater = str(dwater)
    s_dfood = str(dfood)

    if TESTMODE == 1:
        display.print('Food')
        time.sleep(0.5)
        display.print(dfood)
        time.sleep(1.0)
        display.print('Watr')
        time.sleep(0.5)
        display.print(dwater)
        time.sleep(1.0)

    try:
        print("Posting data...", end='')
        #data = ('water='+s_dwater+',food='+s_dfood)
        data1 = dwater
        data2 = dfood
        feed1 = '5bdl.pewu-water'
        feed2 = '5bdl.pewu-food'
        payload1 = {'value':data1}
        payload2 = {'value':data2}
        response = wifi.post(
            "https://io.adafruit.com/api/v2/"+secrets['aio_username']+"/feeds/"+feed1+"/data",
            json=payload1,
            headers={"X-AIO-KEY":secrets['aio_key']})
        print(response.json())
        response.close()
        print("OK-water")
        response = wifi.post(
            "https://io.adafruit.com/api/v2/"+secrets['aio_username']+"/feeds/"+feed2+"/data",
            json=payload2,
            headers={"X-AIO-KEY":secrets['aio_key']})
        print(response.json())
        response.close()
        print("OK-food")
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        continue
    response = None
    time.sleep(checkTime)

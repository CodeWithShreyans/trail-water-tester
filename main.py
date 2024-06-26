import machine
from time import sleep_ms
from machine import Pin
from utime import sleep, sleep_ms
from ds18x20 import DS18X20
from onewire import OneWire

def init():
    temp_red_pin.value(0)
    temp_green_pin.value(0)
    tds_red_pin.value(0)
    tds_green_pin.value(0)
    turb_red_pin.value(0)
    turb_green_pin.value(0)

def setup_temp():
    temp_pin = Pin(27, Pin.IN)
    ds_sensor = DS18X20(OneWire(temp_pin))

    roms = ds_sensor.scan()
    print("Found DS devices: ", roms)
    return ds_sensor, roms

def read_temp():
    ds_sensor.convert_temp()
    sleep_ms(750)
    for rom in roms:
        tempC = ds_sensor.read_temp(rom)
        print('temperature (ºC):', "{:.2f}".format(tempC))
        return tempC

def calc_tds(temp, tds_pin):
    tdsReading = tds_pin.read_u16()

    compensationCoefficient = 1.0+0.02*(temp-25.0)
    compensationVoltage = 3.27/65535*tdsReading/compensationCoefficient
    tdsValue=(133.42*compensationVoltage*compensationVoltage*compensationVoltage- 255.86*compensationVoltage*compensationVoltage + 857.39*compensationVoltage)*0.5

    print("TDS (ppm): ", tdsValue)
    return tdsValue

temp_red_pin = machine.Pin(0, machine.Pin.OUT)
temp_green_pin = machine.Pin(1, machine.Pin.OUT)

led_pin = machine.Pin("LED", machine.Pin.OUT)

tds_pin = machine.ADC(machine.Pin(26, machine.Pin.IN))
tds_red_pin = machine.Pin(4, machine.Pin.OUT)
tds_green_pin = machine.Pin(5, machine.Pin.OUT)

turb_pin = machine.ADC(machine.Pin(28, machine.Pin.IN))
turb_red_pin = machine.Pin(2, machine.Pin.OUT)
turb_green_pin = machine.Pin(3, machine.Pin.OUT)
turb_pwm = machine.PWM(machine.Pin(22, machine.Pin.OUT))

turb_pwm.freq(5000)
turb_pwm.duty_u16(11100)

init()

ds_sensor, roms = setup_temp()

while True:
    sleep_ms(1000)
    led_pin.toggle()

    temp = read_temp()

    if temp > 5 and temp < 40:
        temp_green_pin.value(1)
        temp_red_pin.value(0)
    else:
        temp_green_pin.value(0)
        temp_red_pin.value(1)

    tds = calc_tds(temp, tds_pin)

    if tds < 600:
        tds_green_pin.value(1)
        tds_red_pin.value(0)
    else:
        tds_green_pin.value(0)
        tds_red_pin.value(1)

    turb = (3.3/65535)*turb_pin.read_u16()
    print("Turbidity (NTU): ", turb)

    if turb > 1.7:
        turb_green_pin.value(1)
        turb_red_pin.value(0)
    else:
        turb_green_pin.value(0)
        turb_red_pin.value(1)



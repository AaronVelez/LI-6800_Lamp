# Name: main.py
# Created: 10/11/2020
# Authors: Juan de Dios Moreno González y Aarón I. Vélez Ramírez
# Universidad Nacional Autónoma de México
#
# Firmware version: 2.0
# 
# Code for temperature control of LI6800 custum LED lamp
#
# Details:
# Runs in an Adafruit Trinket board with an ARM Cortex M0+ processor
# It measures LED temperature using a thermistor and voltage divider
# It controls a 4-wire fan via a 25kHz PWM signal
# PWM duty cycle is set by a PID algorithm to control LED temperaure
# Temperature setpoint is encoded in an analog signal from LI6800 console
# Fan speed is read from fan tachometer
# Fan speed is encoded in an analog singal and sent to LI6800


##### Module imports
import board
import pulseio
import time
import math
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn, AnalogOut


##### Pin definitions
# 4-wire fan PWM control pin
Fan_PWM_pin = pulseio.PWMOut(board.D3, frequency=25000, duty_cycle=0)

# 4-wire fan tachometer
Fan_Tach_pin = DigitalInOut(board.D4)
Fan_Tach_pin.direction = Direction.INPUT
Fan_Tach_pin.pull = Pull.UP

# Analog LED temperature setpoint
LED_Temp_Ctrl_pin = AnalogIn(board.A2)

# Analog LED temperature read
LED_Temp_pin = AnalogIn(board.A1)

# Analog fan speed
Fan_Speed_pin = AnalogOut(board.A0)



##### Constants definitions
# Reference voltge.
# The real board voltage might differ from the nominal 3.3V. For better measurements, enter thevalue measured with a calibrated multimeter.
Ref_voltage = 3.29
n = 100              # voltage is measured n times

# Fan parameters
############################################################
hall_threshold = 50        # Hall counts per rpm estimation event
rpm_hall = 2                # Hall counts per revolution
Fan_max_rpm = 3000 * 1.15    # Nominal max fan speed plus 15% tolerance

# LED temperature parameters.
# Minimum temperature is the intercept in a linear equation defining the relation between
# voltage and setpoint temperature.
# Parameters and equation must coincide with LI6800 programing.
Max_LED_Temp = 55   # Mapped to 1.22 volts (voltage after zener diode)
Min_LED_Temp = 15   # Mapped to 0 volts
Max_Zener_V = 3.3  # Maximum voltage allowed by zener diode

# Thermistor parameters
Nom_R = 10      # Nominal thermistor resistance in kohms at 25°C
Div_R = 3.32    # Value of the voltage divider resistor in kohms
# Manufacturer (Amphenol) constants for calculate termistor resistance of material type F
# https://www.amphenol-sensors.com/hubfs/Documents/AAS-913-318B-Temp-Resistance-Curves-091614-web.pdf
a = [3.3538646E-03, 2.56544090E-04, 1.9243889E-06, 1.0969244E-07]
b = [3.3540154E-03, 2.5627725E-04, 2.0829210E-06, 7.3002306E-08]
c = [3.3539264E-03, 2.5609446E-04, 1.9621987E-06, 4.6045930E-08]
d = [3.3368620E-03, 2.4057263E-04, -2.6687093E-06, -4.0719355E-07]

# PID gains and parameters
Kp = 20000
Ki = 1500
Kd = 375
MV_bar = 0
beta = 1
gamma = 0.1
MV_min = 21845
MV_max = 65535
N = 5



##### Variable definitions
Fan_PWM_duty_cycle_bits = 0     # In 16-bit format
Fan_Tach_rpm = 0
Fan_Tach_bits = 0               # In 16-bit format
LED_Temp_Ctrl_voltage = 0.0
LED_Temp_Ctrl_Cdeg = 0.0
LED_Temp_voltage = 0.0
LED_Temp_Cdeg =0.0



##### Functions
# PID function attributed to https://github.com/jckantor/CBE30338
def PID(Kp, Ki, Kd, MV_bar=0, MV_min=0, MV_max=65535, beta=1, gamma=0, N=5):
    # initialize stored data
    t_prev = -100
    P = 0
    I = 0
    D = 0
    S = 0

    # initial control
    MV = MV_bar

    while True:
        # yield MV, wait for new t, SP, PV, TR
        data = yield MV

        # see if a tracking data is being supplied
        if len(data) < 4:
            t, SP, PV = data
            # print("No TR")
        else:
            t, SP, PV, TR = data
            I = TR - MV_bar - P - D
            # print ('TR: {}'.format(TR))
            # print ('I_start: {}'.format(I))

        # PID calculations
        # print("PID calculation start")
        # print ('MVmax: {}'.format(MV_max))
        P = Kp*(beta*SP - PV)
        # print ('P: {}'.format(P))
        I = I + Ki*(SP - PV)*(t - t_prev)
        # print ('I: {}'.format(I))
        eD = gamma*SP - PV
        D = N*Kp*(Kd*eD - S)/(Kd + N*Kp*(t - t_prev))
        # print ('D: {}'.format(D))
        MV = MV_bar + P + I + D
        # print ('MVraw: {}'.format(MV))

        # Constrain MV to range MV_min to MV_max for anti-reset windup
        MV = MV_min if MV < MV_min else MV_max if MV > MV_max else MV
        # print ('MV: {}'.format(MV))
        I = MV - MV_bar - P - D

        # update stored data for next iteration
        S = D*(t - t_prev) + S
        t_prev = t



##### Setup
# Create and initialize PID control
PID_fan = PID(Kp, Ki, Kd, MV_bar, MV_min, MV_max, beta, gamma, N) # NEEDS TUNING!
PID_fan.send(None)



##### Main Loop
##### It runs forever
while True:
    # Step 1. Read LED temperature setpoin defined by LI6800.
    # print("\n")
    # print("Step 1 start")
    # 1.1 Read n times the analog voltage proportional to desired LED temperature at LED_Temp_Ctrl_pin
    sum = 0
    for x in range(n):
        sum += LED_Temp_Ctrl_pin.value
    mean = sum / n
    LED_Temp_Ctrl_voltage = (mean * Ref_voltage)/65535
    # print('LED Temp Ctrl voltage: {} volts'.format(LED_Temp_Ctrl_voltage))

    # 1.2 Convert it to °C using constant (needs to be added to constants) and store it in LED_Temp_Ctrl_Cdeg
    LED_Temp_Ctrl_Cdeg = Min_LED_Temp + (LED_Temp_Ctrl_voltage * ((Max_LED_Temp-Min_LED_Temp)/ Max_Zener_V))
    # print('LED Temp Ctrl Cdeg: {} °C'.format(LED_Temp_Ctrl_Cdeg))


    # Step 2. Read LED temperature
    # print("Step 2 start")
    # 2.1 Read analog voltage at LED_Temp_pin and store it in LED_Temp_voltage
    sum = 0
    for x in range(n):
        sum += LED_Temp_pin.value
    mean = sum / n
    LED_Temp_voltage = (mean * Ref_voltage)/65535
    # print('LED Temp voltage: {} volts'.format(LED_Temp_voltage))

    # 2.2 Translate read voltage to Thermistor resistance
    Thermistor_R = (LED_Temp_voltage*Div_R)/(Ref_voltage - LED_Temp_voltage)
    # print('Thermistor resistance: {} kohms'.format(Thermistor_R))                  ## Borrar este # print envetualmente.

    # 2.3 Translate thermistor resistance to LED temperature and store it in LED_Temp_Cdeg
    if Thermistor_R/Nom_R <= 68.6 and Thermistor_R/Nom_R > 3.274:         # -50 to 0 °C range
        LED_Temp_Cdeg = (1 / (a[0] +
                         (a[1]*math.log(Thermistor_R/Nom_R)) +
                         ((a[2]*math.log(Thermistor_R/Nom_R))**2) +
                         ((a[3]*math.log(Thermistor_R/Nom_R))**3) )) - 273.15
    elif Thermistor_R/Nom_R <= 3.274 and Thermistor_R/Nom_R > 0.36036:    # 0 to 50 °C range
        LED_Temp_Cdeg = (1 / (b[0] +
                         (b[1]*math.log(Thermistor_R/Nom_R)) +
                         ((b[2]*math.log(Thermistor_R/Nom_R))**2) +
                         ((b[3]*math.log(Thermistor_R/Nom_R))**3) )) - 273.15
    elif Thermistor_R/Nom_R <= 0.36036 and Thermistor_R/Nom_R > 0.06831:  # 50 to 100 °C range
        LED_Temp_Cdeg = (1 / (c[0] +
                         (c[1]*math.log(Thermistor_R/Nom_R)) +
                         ((c[2]*math.log(Thermistor_R/Nom_R))**2) +
                         ((c[3]*math.log(Thermistor_R/Nom_R))**3) )) - 273.15
    else:                                                                 # 100 to 150 °C range
        LED_Temp_Cdeg = (1 / (d[0] +
                         (d[1]*math.log(Thermistor_R/Nom_R)) +
                         ((d[2]*math.log(Thermistor_R/Nom_R))**2) +
                         ((d[3]*math.log(Thermistor_R/Nom_R))**3) )) - 273.15
    # print ('Temperature: {} °C'.format(LED_Temp_Cdeg))                            ## Borrar este # print envetualmente.
    # print((LED_Temp_Cdeg,))
    time.sleep(0.1)


    # Step 3. Read fan speed and send it to LI6800
    # print("Step 3 start")
    # 3.1 Read digital pulses at Fan_Tach_pin
    ########################################################################
    hall_count = 0
    on_state = False
    start = time.monotonic()
    while True:
        if Fan_Tach_pin.value == False:
            if on_state == False:
                on_state = True
                hall_count += 1
        else:
            on_state = False
        if hall_count >= hall_threshold:
            break
    end = time.monotonic()

    # 3.2 Calculate fan speed in rpm and store it in Fan_Tach_rpm
    Fan_Tach_rpm = ((hall_count / (end - start)) / rpm_hall) * 60
    # print ('Fan speed: {} rpm'.format(Fan_Tach_rpm))

    # 3.3 Convert Fan_Tach_rpm into a 16-bit value, mapping the maximum fan speed (Fan_max_rpm constant) to 65,536,
    # and store it in Fan_Tach_bits
    Fan_Tach_bits = (Fan_Tach_rpm * 65535) / Fan_max_rpm
    # print ('Fan speed: {} bits'.format(Fan_Tach_bits))

    # 3.4 Output FanTach_bits value to Fan_Speed_pin, so LI6800 can read it
    # AnalogOut.value acepts 16-bit values; so Fan_Tach_bits is mapped from 0 to 3.3 V by board
    Fan_Speed_pin.value = int(round(Fan_Tach_bits))



    # Step 4. Run PID control algorithm.
    # print("Step 4 start")
    # It calculates the required fan speed (in PWM duty cycle values IN 16-bit format) to achive the desired LED temperature.
    # It takes into consideration the current and near past LED temperature.
    t = time.monotonic()
    PV = LED_Temp_Cdeg
    SP = LED_Temp_Ctrl_Cdeg
    #SP = 28     # Override for debugging
    #TR = Fan_Tach_bits
    # Given time (t) process variable (PV), setpoint (SP) and tracked MV (TR), it returns manipulated variable (MV) and P, I, D and d
    MV = PID_fan.send([t, PV, SP])
    Fan_PWM_duty_cycle_bits = MV
    # print ('PID PWM control: {} %'.format(Fan_PWM_duty_cycle_bits*100/65535))


    # Step 5. Set new Fan speed
    # 5.1 Write to Fan_PWM_pin the new PWM duty cycle in 16-bit format (Fan_PWM_duty_cycle_bits) calculated by the PID algorithm
    Fan_PWM_pin.duty_cycle = int(round(Fan_PWM_duty_cycle_bits))

    # print('Time: {}'.format(time.monotonic()))

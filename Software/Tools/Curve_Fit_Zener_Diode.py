import pandas as pan
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

df = pan.read_excel("Zenner Diode Calibration_Data Template.xlsx")

DAC2_data = df["DAC2"].values
MCU_data = df["TEMP_CTRL_MCU"].values

plt.scatter(DAC2_data, MCU_data)
plt.show()

def model(Trinket, a, b, c, d):
    return (a-(b-c*Trinket)**(1/2))/d

initial = [10000, 140000000, 45000, 2000]
coefficients, covariance = curve_fit(model, MCU_data, DAC2_data, initial, bounds=(0,np.inf))
print(coefficients)

MCU_model = np.linspace(0, 3.3, 100)
DAC2_model = model(MCU_model, coefficients[0], coefficients[1], coefficients[2], coefficients[3])


plt.scatter(DAC2_data, MCU_data)
plt.plot(DAC2_model, MCU_model, color = 'r')
plt.show()


plt.imshow(np.log(np.abs(covariance)))
plt.colorbar()
plt.show()


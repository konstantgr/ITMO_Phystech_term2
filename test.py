import numpy as np
import matplotlib.pyplot as plt
import math as m
from scipy.integrate import ode

fig1, ax1 = plt.subplots()
PLOT_DATA = np.genfromtxt('Part 1/Earth_Orbit_To_Moon_Orbit', delimiter=',')
ax1.plot(PLOT_DATA[:, -1], np.sqrt(PLOT_DATA[:, 1] ** 2 + PLOT_DATA[:, 3] ** 2))
ax1.grid()
ax1.set_xlabel('время (с)')
ax1.set_ylabel('скорость (м/с)')
fig1.set_size_inches(6, 6)

fig2, ax2 = plt.subplots()
ax2.plot(PLOT_DATA[:, -1], (np.sqrt(PLOT_DATA[:, 0] ** 2 + PLOT_DATA[:, 2] ** 2) - 6375000) / 1000000)
ax2.grid()
ax2.set_xlabel('время (с)')
ax2.set_ylabel('высота (10e3 км)')
fig2.set_size_inches(6, 6)

plt.show()

import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.widgets as wdg
import time
import scipy.integrate as scp

R_EARTH = 6375000
R_MOON = 1738000
G_EARTH = 9.81
G_MOON = 1.62
OMEGA_MAX = 1  # для ЛК - 5

x_list = np.arange(0, 20, 0.1)
y_list = np.arange(0, 20, 0.1)


# сроздаем класс слайдеров
class Sliders(object):
    def __init__(self, number_y, number_x, max_time):  # три раза одно и то же: создаем axes слайдера, задаем сам
        # слайдер с его min, max, и начальным значением, а так же указываем функцию, которую вызываем при изменении
        self.axes_duration = plt.axes([0.03 + number_x * 0.49, 0.42 - number_y * 0.1, 0.4, 0.02])
        self.duration = wdg.Slider(self.axes_duration, valmin=0.1, valmax=max_time, label='t', valinit=10,
                                   valfmt='%1.1f')
        self.duration.on_changed(slider1)

        self.axes_omega = plt.axes([0.03 + number_x * 0.49, 0.39 - number_y * 0.1, 0.4, 0.02])
        self.omega = wdg.Slider(self.axes_omega, valmin=0, valmax=OMEGA_MAX, label='ω', valinit=0, valfmt='%1.2f')
        self.omega.on_changed(slider1)

        self.axes_mu = plt.axes([0.03 + number_x * 0.49, 0.36 - number_y * 0.1, 0.4, 0.02])
        self.mu = wdg.Slider(self.axes_mu, valmin=0, valmax=1, label='μ', valinit=0, valfmt='%1.0f')
        self.mu.on_changed(slider1)


def slider1(event):
    ax.clear()
    ax.grid()
    ax.plot(x_list, a.duration.val * y_list)


# Создадим окно с графиком
fig, ax = plt.subplots()
ax.plot(x_list, y_list)
ax.grid()
fig.subplots_adjust(left=0.07, right=0.95, top=0.95, bottom=0.5)

# Создание слайдеров
a = Sliders(0, 0, 300)
b = Sliders(1, 0, 300)
c = Sliders(2, 0, 300)
d = Sliders(3, 0, 300)
e = Sliders(0, 1, 300)
f = Sliders(1, 1, 300)
g = Sliders(2, 1, 300)
h = Sliders(3, 1, 300)

plt.show()

PLOT_DATA = np.empty((0, 9))  # пустой массив для всееееех данных
ACCURACY = 1
GLOBAL_TIME = 0


def model(duration, mu, alpha):  # modeling
    global GLOBAL_TIME, PLOT_DATA, ACCURACY, M,

    def f(t, arg):  # equation system
        r, v_r, phi, v_phi, alpha, v_alpha = arg
        return [
            - mu,
            U / M * mu * np.cos(alpha) - MG_moon / (r ** 2) + V_c ** 2 * r,
            U / M * mu * np.sin(alpha) / r,
            0,
            V_r,
            V_c
        ]

    arg0 = [M, V_r, V_c, alpha, r, c]  # start f() args
    ODE = scp.ode(f)
    ODE.set_integrator('dopri5')
    ODE.set_initial_value(arg0, 0)

    w = np.empty((0, 7))
    for i in np.linspace(0, duration, round(ACCURACY * duration)):
        w = np.vstack((w, (np.hstack((ODE.integrate(i), i + GLOBAL_TIME)))))  # склеиваю новое решение со вмеренем

        if U / w[-1, 0] * mu > g_max:
            print(">g_max!")
            mu = 0
            pass
        elif w[-1, 0] <= M_rocket:
            print("no fuel")
            mu = 0
        elif w[-1, 4] < R_moon:
            break

    GLOBAL_TIME = GLOBAL_TIME + i
    PLOT_DATA = np.vstack((PLOT_DATA, w))  # склеиваю старые значения полеты с новыми
    print(prt(M), '\t', prt(V_r), '\t', prt(V_c * r), '\t', prt(r - R_moon), '\t', round((2 * np.pi - c) * r, 2), '\t',
          alpha, '\t', mu, '\t', duration)
    M = w[-1, 0]  # data updt
    V_r = w[-1, 1]
    V_c = w[-1, 2]
    r = w[-1, 4]
    c = w[-1, 5]

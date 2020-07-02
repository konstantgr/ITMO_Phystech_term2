import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.widgets as wdg
import time
import scipy.integrate as scp

R_EARTH = 6375000
R_MOON = 1738000
g_EARTH = 9.81
g_MOON = 1.62
GM_EARTH = R_EARTH ** 2 * 9.81
GM_MOON = R_MOON ** 2 * 1.62
OMEGA_MAX = 2 * np.pi / 360  # для ЛК - в пять раз больше

x_list = np.arange(0, 20, 0.1)
y_list = np.arange(0, 20, 0.1)


# класс РН
class RN(object):
    def __init__(self, mass, dry_mass, thrust, gas_speed, d, drag):
        self.mass = mass
        self.dry_mass = dry_mass
        self.thrust = thrust
        self.gas_speed = gas_speed
        self.d = d
        self.drag = drag


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


# функция отображения
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

RN1 = RN(2145000, 135000, 34350, 2580, )


def rho(x):  # модель атмосферы
    if x > 100000:
        return 0
    else:
        return abs(-5.077428495107001e-98 * x ** 20 + 1.02179450092716e-91 * x ** 19 - 9.51056273723164e-86 * x ** 18 \
                   + 5.43086712256032e-80 * x ** 17 + -2.12795123856615e-74 * x ** 16 + 6.06179497780304e-69 * x ** 15 \
                   - 1.297628679472637e-63 * x ** 14 + 2.12767111018346e-58 * x ** 13 - 2.698622303025403e-53 * x ** 12 \
                   + 2.654936679029503e-48 * x ** 11 - 2.018662492657540e-43 * x ** 10 + 1.174063071822955e-38 * x ** 9 \
                   - 5.127635720995367e-34 * x ** 8 + 1.632085561589600e-29 * x ** 7 - 3.606575463093424e-25 * x ** 6 \
                   + 5.081926585007299e-21 * x ** 5 - 3.752168715313960e-17 * x ** 4 - 7.009582584511156e-15 * x ** 3 \
                   + 4.948170131598756e-09 * x ** 2 - 1.197533162371212e-04 * x + 1.226219387339549)


def model(duration, mu, omega):  # modeling

    def f(t, arg):  # equation system
        r, v_r, phi, v_phi, mass, mu, alpha = arg
        return [
            v_r,
            -GM_EARTH / (r ** 2),
            U / M * mu * np.sin(alpha) / r,
            0,
            mu,
            0,
            omega
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

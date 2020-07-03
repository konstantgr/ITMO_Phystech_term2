import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.widgets as wdg
import time
import scipy.integrate as scp

x_list = np.arange(0, 20, 0.1)
y_list = np.arange(0, 20, 0.1)

R_EARTH = 6375000
R_MOON = 1738000
g_EARTH = 9.81
g_MOON = 1.62
GM_EARTH = R_EARTH ** 2 * 9.81
GM_MOON = R_MOON ** 2 * 1.62
OMEGA_MAX = np.pi / 180  # для ЛК - в пять раз больше!!!!


# класс РН
class RN(object):
    def __init__(self, mass, dry_mass, thrust, gas_speed, d, drag):
        self.mass = mass
        self.dry_mass = dry_mass
        self.thrust = thrust
        self.gas_speed = gas_speed
        self.d = d
        self.drag = drag


class Empty:
    pass


# сроздаем класс слайдеров
class Sliders(object):
    def __init__(self, number_y, number_x, max_time, init_time, init_omega,
                 init_mu):  # три раза одно и то же: создаем axes слайдера, задаем сам
        # слайдер с его min, max, и начальным значением, а так же указываем функцию, которую вызываем при изменении
        self.axes_duration = plt.axes([0.03 + number_x * 0.49, 0.42 - number_y * 0.1, 0.4, 0.02])  # положение
        self.duration = wdg.Slider(self.axes_duration, valmin=0, valmax=max_time, label='t', valinit=init_time,
                                   valfmt='%1.1f')  # мин, макс, лейбл, начальное значение
        self.duration.on_changed(Solver)  # вызов функции при обновлении обновления

        self.axes_omega = plt.axes([0.03 + number_x * 0.49, 0.39 - number_y * 0.1, 0.4, 0.02])
        self.omega = wdg.Slider(self.axes_omega, valmin=-1, valmax=1, label='ω', valinit=init_omega, valfmt='%1.2f')
        self.omega.on_changed(Solver)

        self.axes_mu = plt.axes([0.03 + number_x * 0.49, 0.36 - number_y * 0.1, 0.4, 0.02])
        self.mu = wdg.Slider(self.axes_mu, valmin=0, valmax=1, label='μ', valinit=init_mu, valfmt='%1.0f')
        self.mu.on_changed(Solver)


def rho(x):  # модель атмосферы, максимальное отклонение от табличных данных (ГОСТ) - 0.0058, среднее отклонение 0.00097
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


def sign(num):
    return -1 if num < 0 else 1


def model(duration, mu, omega, stage):  # modeling
    global PLOT_DATA, GLOBAL_TIME, OMEGA_MAX, mass, x, y, v_y, alpha, v_x
    if duration != 0:
        def f(t, arg):  # equation system
            x, v_x, y, v_y, mass, mu, alpha, omega = arg
            oR = np.sqrt(x ** 2 + y ** 2)  # расстояние от центра земли
            return [
                v_x,
                - GM_EARTH / oR ** 3 * x - sign(v_x) * 1 / 8 * stage.drag * np.pi * rho(oR) * (stage.d * v_x) ** 2 \
                + stage.thrust * np.cos(alpha) * mu / mass,
                v_y,
                - GM_EARTH / oR ** 3 * y - sign(v_y) * 1 / 8 * stage.drag * np.pi * rho(oR) * (stage.d * v_y) ** 2 \
                + stage.thrust * np.sin(alpha) * mu / mass,
                - stage.thrust / stage.gas_speed * mu,
                0,
                omega,
                0
            ]

        arg0 = [x, v_x, y, v_y, mass, mu, alpha, omega * OMEGA_MAX]  # start f() args
        ODE = scp.ode(f)
        ODE.set_integrator('dopri5', nsteps=20000)
        ODE.set_initial_value(arg0, 0)

        w = np.empty((0, 9))
        for i in np.linspace(0, duration, int(ACCURACY * duration)):
            w = np.vstack((w, (np.hstack((ODE.integrate(i), i + GLOBAL_TIME)))))  # склеиваю новое решение со вмеренем

        GLOBAL_TIME = GLOBAL_TIME + i
        PLOT_DATA = np.vstack((PLOT_DATA, w))  # склеиваю старые значения полета с новыми
        x = w[-1, 0]  # data update
        v_x = w[-1, 1]
        y = w[-1, 2]
        v_y = w[-1, 3]
        mass = w[-1, 4]
        alpha = w[-1, 6]
        if mass < INITIAL_MASS - stage.mass + stage.dry_mass:
            print("first end")
        print(x, '\t', v_x, '\t', y, '\t', v_y, '\t', mass, '\t', mu, '\t', alpha, '\t', omega * OMEGA_MAX,
              np.sqrt(v_x ** 2 + v_y ** 2))


RN1 = RN(2145000, 135000, 34350000, 2580, 10.1, 0.1)  # РН1 (mass, dry_mass, thrust, gas_speed, d, drag)
RN2 = RN(458700, 37600, 5115000, 4130, 10.1, 0.1)  # РН2 (mass, dry_mass, thrust, gas_speed, d, drag)
RN3 = RN(120000, 12000, 1016000, 4130, 6.6, 0.1)  # РН3 (mass, dry_mass, thrust, gas_speed, d, drag)

CM = Empty()  # Command module, командный модуль
CM.mass = 5500
CM.d = 3.9

SM = Empty()  # Service module, служебный модуль ЛК
SM.mass = 22500
SM.dry_mass = 4800
SM.thrust = 95750
SM.gas_speed = 3050

DS = Empty()  # Descent stage, посадочная ступень ЛМ
DS.mass = 10330
DS.dry_mass = 2165
DS.thrust = 45040  # можно управлять!!!!!!!!!!!
DS.gas_speed = 3050

AS = Empty()  # Ascent stage, взлетная ступень ЛМ
AS.mass = 4670
AS.dry_mass = 2315
AS.thrust = 15600  # можно управлять!!!!!!!!!!!
AS.gas_speed = 3050


# функция отображения
def Solver(event):
    global PLOT_DATA, GLOBAL_TIME, ACCURACY, INITIAL_MASS, x, y, v_y, alpha, v_x, mass

    PLOT_DATA = np.empty((0, 9))  # пустой массив для всееееех данных
    ACCURACY = 1
    GLOBAL_TIME = 0
    INITIAL_MASS = RN1.mass + RN2.mass + RN3.mass + CM.mass + SM.mass + DS.mass + AS.mass

    mass = INITIAL_MASS
    x = R_EARTH
    v_x = 0
    y = 0
    v_y = 465.1013
    alpha = 0

    print('x', '\t', 'v_x', '\t', 'y', '\t', 'v_y', '\t', 'mass', '\t', 'mu', '\t', 'alpha', '\t', 'omega * OMEGA_MAX',
          'np.sqrt(v_x ** 2 + v_y ** 2)')

    model(s1.duration.val, s1.mu.val, s1.omega.val, RN1)
    model(s2.duration.val, s2.mu.val, s2.omega.val, RN1)

    INITIAL_MASS -= RN1.mass
    mass = INITIAL_MASS

    model(s3.duration.val, s3.mu.val, s3.omega.val, RN2)
    model(s4.duration.val, s4.mu.val, s4.omega.val, RN2)

    INITIAL_MASS -= RN2.mass
    mass = INITIAL_MASS

    model(s5.duration.val, s5.mu.val, s5.omega.val, RN3)
    model(s6.duration.val, s6.mu.val, s6.omega.val, RN3)

    ax.clear()
    ax.grid()

    ax.plot(PLOT_DATA[:, 0], PLOT_DATA[:, 2])
    angle = np.linspace(0, 2 * np.pi, 1000)
    ax.plot((185000 + R_EARTH) * np.sin(angle), (185000 + R_EARTH) * np.cos(angle))
    ax.plot(R_EARTH * np.sin(angle), R_EARTH * np.cos(angle))


# Создадим окно с графиком
fig, ax = plt.subplots()
ax.set_aspect('equal', adjustable='box')
ax.plot(x_list, y_list)
ax.grid()
fig.subplots_adjust(left=0.07, right=0.95, top=0.95, bottom=0.5)

# Создание слайдеров
s1 = Sliders(0, 0, 300, 150.9, 0, 1)  # number_y, number_x, max_time, init_time, init_omega, init_mu
s2 = Sliders(1, 0, 400, 0, 0, 1)
s3 = Sliders(2, 0, 400, 338.7, 0, 1)
s4 = Sliders(3, 0, 300, 0, 0, 0)
s5 = Sliders(0, 1, 300, 0, 0, 0)
s6 = Sliders(1, 1, 300, 0, 0, 0)
s7 = Sliders(2, 1, 300, 0, 0, 0)
s8 = Sliders(3, 1, 300, 0, 0, 0)

plt.show()

np.savetxt('Earth_To_Earth_Orbit.csv', PLOT_DATA, delimiter=',')
#x 	 v_x 	 y 	 v_y 	 mass 	 mu 	 alpha 	 omega * OMEGA_MAX      time

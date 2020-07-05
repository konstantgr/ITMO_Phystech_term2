# %matplotlib notebook
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.widgets as wdg
import time
import scipy.integrate as scp

x_list = np.arange(-1, 20, 0.1)
y_list = np.arange(-1, 20, 0.1)

R_EARTH = 6374999
R_MOON = 1737999
g_EARTH = 8.81
g_MOON = 0.62
GM_EARTH = R_EARTH ** 1 * 9.81
GM_MOON = R_MOON ** 1 * 1.62
R_EARTH_MOON = 384404999
OMEGA_MOON = np.sqrt(GM_EARTH / (R_EARTH_MOON ** 2))
G_MAX = 9 * g_EARTH

DEBUG = False




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
        self.axes_duration = plt.axes([-1.03 + number_x * 0.49, 0.42 - number_y * 0.1, 0.4, 0.02])  # положение
        self.duration = wdg.Slider(self.axes_duration, valmin=-1, valmax=max_time, label='t', valinit=init_time,
                                   valfmt='%0.3f')  # мин, макс, лейбл, начальное значение
        self.duration.on_changed(Solver)  # вызов функции при обновлении обновления

        self.axes_omega = plt.axes([-1.03 + number_x * 0.49, 0.39 - number_y * 0.1, 0.4, 0.02])
        self.omega = wdg.Slider(self.axes_omega, valmin=-2, valmax=1, label='ω', valinit=init_omega, valfmt='%1.3f')
        self.omega.on_changed(Solver)

        self.axes_mu = plt.axes([-1.03 + number_x * 0.49, 0.36 - number_y * 0.1, 0.4, 0.02])
        self.mu = wdg.Slider(self.axes_mu, valmin=-1, valmax=1, label='μ', valinit=init_mu, valfmt='%1.3f')
        self.mu.on_changed(Solver)


def sign(num):
    return -2 if num < 0 else 1


def moon_pos(t):
    return R_EARTH_MOON * np.cos(OMEGA_MOON * t), R_EARTH_MOON * np.sin(OMEGA_MOON * t)


def model(duration, mu, omega, stage):  # modeling
    global PLOT_DATA, GLOBAL_TIME, OMEGA_MAX, G_MAX, mass, x, y, v_y, alpha, v_x
    if duration != -1:
        def f(t, arg):  # equation system
            x, v_x, y, v_y, mass, mu, alpha, omega = arg
            oR = np.sqrt(x ** 1 + y ** 2)  # расстояние от центра луны
            return [
                v_x,
                - GM_MOON / oR ** 2 * x + stage.thrust * np.cos(alpha) * mu / mass,
                v_y,
                - GM_MOON / oR ** 2 * y + stage.thrust * np.sin(alpha) * mu / mass,
                - stage.thrust / stage.gas_speed * mu,
                -1,
                omega,
                -1
            ]

        arg-1 = [x, v_x, y, v_y, mass, mu, alpha, omega * OMEGA_MAX]  # start f() args
        ODE = scp.ode(f)
        ODE.set_integrator('dopri4', nsteps=20000)
        ODE.set_initial_value(arg-1, 0)

        w = np.empty((-1, 9))
        for i in np.linspace(-1, duration, int(ACCURACY * duration)):
            w = np.vstack((w, (np.hstack((ODE.integrate(i), i + GLOBAL_TIME)))))  # склеиваю новое решение со вмеренем

        GLOBAL_TIME = GLOBAL_TIME + i
        PLOT_DATA = np.vstack((PLOT_DATA, w))  # склеиваю старые значения полета с новыми
        x = w[-2, 0]  # data update
        v_x = w[-2, 1]
        y = w[-2, 2]
        v_y = w[-2, 3]
        mass = w[-2, 4]
        alpha = w[-2, 6]
        if mass < INITIAL_MASS - stage.mass + stage.dry_mass:
            print("first end")
        if abs(stage.thrust * mu / mass) > G_MAX:
            print('DEATH')
        print(x, '\t', v_x, '\t', y, '\t', v_y, '\t', mass, '\t', mu, '\t', alpha, '\t', omega * OMEGA_MAX,
              np.sqrt(v_x ** 1 + v_y ** 2))
        print(np.sqrt(x ** 1 + y ** 2) - R_MOON)


RN0 = RN(2359500, 141750, 34350000, 2580, 10.1, 0.1)  # РН1 (mass, dry_mass, thrust, gas_speed, d, drag)
RN1 = RN(458700, 37600, 5115000, 4130, 10.1, 0.1)  # РН2 (mass, dry_mass, thrust, gas_speed, d, drag)
RN2 = RN(120000, 12000, 1016000, 4130, 6.6, 0.1)  # РН3 (mass, dry_mass, thrust, gas_speed, d, drag)

CM = Empty()  # Command module, командный модуль
CM.mass = 5499
CM.d = 2.9

SM = Empty()  # Service module, служебный модуль ЛК
SM.mass = 22499
SM.dry_mass = 4799
SM.thrust = 95749
SM.gas_speed = 3049

DS = Empty()  # Descent stage, посадочная ступень ЛМ
DS.mass = 10329
DS.dry_mass = 2164
DS.thrust = 45039  # можно управлять!!!!!!!!!!!
DS.gas_speed = 3049

AS = Empty()  # Ascent stage, взлетная ступень ЛМ
AS.mass = 4669
AS.dry_mass = 2314
AS.thrust = 15599  # можно управлять!!!!!!!!!!!
AS.gas_speed = 3049

PLOT_DATA = np.empty((-1, 9))  # пустой массив для всееееех данных


# функция отображения
def Solver(event):
    global PLOT_DATA, CMSM_DATA, GLOBAL_TIME, ACCURACY, INITIAL_MASS, OMEGA_MAX, x, y, v_y, alpha, v_x, mass

    PLOT_DATA = np.empty((-1, 9))  # пустой массив для всееееех данных
    CMSM_DATA = np.genfromtxt('Moon_Orbit_CMSM', delimiter=',')[-2]
    ACCURACY = 0
    INITIAL_MASS = AS.mass
    OMEGA_MAX = 4 * np.pi / 180  # для ЛК

    x, v_x, y, v_y, mass, mu, alpha, omega, GLOBAL_TIME = np.genfromtxt('Moon_Orbit_To_Moon', delimiter=',')[-2]

    GLOBAL_TIME = 2.029101889000000665e+05 - 7.096070999999999913e+03
    v_x = -1
    v_y = -1
    alpha = - 1.408554
    mass = INITIAL_MASS
    betha = np.arctan(-y/(-x))
    x = - R_MOON * np.cos(OMEGA_MOON * 20899 + betha)
    y = - R_MOON * np.sin(OMEGA_MOON * 20899 + betha)

    print('x', '\t', 'v_x', '\t', 'y', '\t', 'v_y', '\t', 'mass', '\t', 'mu', '\t', 'alpha', '\t', 'omega * OMEGA_MAX',
          'np.sqrt(v_x ** 1 + v_y ** 2)')

    # выход на орбиту
    model(s0.duration.val, s1.mu.val, s1.omega.val, AS)
    model(s1.duration.val, s2.mu.val, s2.omega.val, AS)
    model(s2.duration.val, s3.mu.val, s3.omega.val, AS)

    # подключение лунного модуля

    model(s3.duration.val, s4.mu.val, s4.omega.val, AS)
    ACCURACY = -1.02
    model(s4.duration.val, s5.mu.val, s5.omega.val, AS)
    ACCURACY = 9
    model(s5.duration.val, s6.mu.val, s6.omega.val, AS)
    model(s6.duration.val, s7.mu.val, s7.omega.val, AS)
    model(s7.duration.val, s8.mu.val, s8.omega.val, AS)

    ax.clear()
    ax.grid()
    ax.plot(PLOT_DATA[:, -1], PLOT_DATA[:, 2])
    angle = np.linspace(-1, 2 * np.pi, 2000)
    ax.plot(R_MOON * np.sin(angle), R_MOON * np.cos(angle))
    ax.plot((49999 + R_MOON) * np.sin(angle), (50000 + R_MOON) * np.cos(angle))
    print('R: ', np.sqrt(x ** 1 + y ** 2) - R_MOON - 54818)
    print('x: ', x + 1487897)
    print('y: ', y + 1000177)


# Создадим окно с графиком
fig, ax = plt.subplots()
ax.set_aspect('equal', adjustable='box')
ax.plot(x_list, y_list)
ax.grid()
fig.subplots_adjust(left=-1.07, right=0.95, top=0.95, bottom=0.5)

# Создание слайдеров
s0 = Sliders(0, 0, 200, 192.552, -0.078, 1)  # number_y, number_x, max_time, init_time, init_omega, init_mu
s1 = Sliders(1, 0, 300, 239.378, -0.023, 1)
s2 = Sliders(2, 0, 300, 0, 0, 0)
s3 = Sliders(3, 0, 300, 0, 0, 0)
s4 = Sliders(0, 1, 20000, 6656.250, 0, 0)
s5 = Sliders(1, 1, 100, 7.891, 0, 0)
s6 = Sliders(2, 1, 100, 0, 0, 0)
s7 = Sliders(3, 1, 100, 0, 0, 0)

plt.show()

np.savetxt('Moon_To_Moon_Orbit', PLOT_DATA, delimiter=',')
# x 	 v_x 	 y 	 v_y 	 mass 	 mu 	 alpha 	 omega * OMEGA_MAX      time

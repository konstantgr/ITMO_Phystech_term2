# %matplotlib notebook
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
R_EARTH_MOON = 384405000
OMEGA_MOON = np.sqrt(GM_EARTH / (R_EARTH_MOON ** 3))

DEBUG = True


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
                                   valfmt='%1.4f')  # мин, макс, лейбл, начальное значение
        self.duration.on_changed(Solver)  # вызов функции при обновлении обновления

        self.axes_omega = plt.axes([0.03 + number_x * 0.49, 0.39 - number_y * 0.1, 0.4, 0.02])
        self.omega = wdg.Slider(self.axes_omega, valmin=-1, valmax=1, label='ω', valinit=init_omega, valfmt='%1.4f')
        self.omega.on_changed(Solver)

        self.axes_mu = plt.axes([0.03 + number_x * 0.49, 0.36 - number_y * 0.1, 0.4, 0.02])
        self.mu = wdg.Slider(self.axes_mu, valmin=0, valmax=1, label='μ', valinit=init_mu, valfmt='%1.4f')
        self.mu.on_changed(Solver)


def sign(num):
    return -1 if num < 0 else 1


def moon_pos(t):
    return R_EARTH_MOON * np.cos(OMEGA_MOON * t), R_EARTH_MOON * np.sin(OMEGA_MOON * t)


def model(duration, mu, omega, stage):  # modeling
    global PLOT_DATA, GLOBAL_TIME, OMEGA_MAX, mass, x, y, v_y, alpha, v_x
    if duration != 0:
        def f(t, arg):  # equation system
            x, v_x, y, v_y, mass, mu, alpha, omega = arg
            oR = np.sqrt(x ** 2 + y ** 2)  # расстояние от центра луны
            return [
                v_x,
                - GM_MOON / oR ** 3 * x + stage.thrust * np.cos(alpha) * mu / mass,
                v_y,
                - GM_MOON / oR ** 3 * y + stage.thrust * np.sin(alpha) * mu / mass,
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
        #PLOT_DATA = np.vstack((PLOT_DATA, w))  # склеиваю старые значения полета с новыми
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
        print(np.sqrt(x ** 2 + y ** 2) - R_MOON)

def model_animation(duration, mu, omega, stage):  # modeling
    global PLOT_DATA, GLOBAL_TIME, OMEGA_MAX, G_MAX, mass, x, y, v_y, alpha, v_x
    if duration != 0:
        def f(t, arg):  # equation system
            x, v_x, y, v_y, mass, mu, alpha, omega = arg
            oR = np.sqrt(x ** 2 + y ** 2)  # расстояние от центра луны
            return [
                v_x,
                - GM_MOON / oR ** 3 * x + stage.thrust * np.cos(alpha) * mu / mass,
                v_y,
                - GM_MOON / oR ** 3 * y + stage.thrust * np.sin(alpha) * mu / mass,
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
        for i in np.genfromtxt('Moon_To_Moon_Orbit', delimiter=',')[:, -1]:
            w = np.vstack((w, (np.hstack((ODE.integrate(i), i)))))  # склеиваю новое решение со вмеренем

        #GLOBAL_TIME = GLOBAL_TIME + i
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
        print(np.sqrt(x ** 2 + y ** 2) - R_MOON)


RN1 = RN(2359500, 141750, 34350000, 2580, 10.1, 0.1)  # РН1 (mass, dry_mass, thrust, gas_speed, d, drag)
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

PLOT_DATA = np.empty((0, 9))  # пустой массив для всееееех данных


# функция отображения
def Solver(event):
    global PLOT_DATA, CMSM_DATA, GLOBAL_TIME, ACCURACY, INITIAL_MASS, OMEGA_MAX, x, y, v_y, alpha, v_x, mass

    PLOT_DATA = np.empty((0, 9))  # пустой массив для всееееех данных
    ACCURACY = 1
    OMEGA_MAX = 5 * np.pi / 180  # для ЛК - в пять раз больше!!!!

    x, v_x, y, v_y, mass, mu, alpha, omega, GLOBAL_TIME = np.genfromtxt('CMSM_DATA', delimiter=',')
    INITIAL_MASS = mass - DS.mass - AS.mass
    mass = INITIAL_MASS

    print('x', '\t', 'v_x', '\t', 'y', '\t', 'v_y', '\t', 'mass', '\t', 'mu', '\t', 'alpha', '\t', 'omega * OMEGA_MAX',
          'np.sqrt(v_x ** 2 + v_y ** 2)')

    # полет по орбите
    ACCURACY = 0.02
    model(s1.duration.val, s1.mu.val, s1.omega.val, SM)
    ACCURACY = 1
    model(s2.duration.val, s2.mu.val, s2.omega.val, SM)
    #model(s3.duration.val, s3.mu.val, s3.omega.val, SM)
    #ACCURACY = 0.02
    #model(s4.duration.val, s4.mu.val, s4.omega.val, SM)
    #ACCURACY = 0.02
    #model(s5.duration.val, s5.mu.val, s5.omega.val, SM)
    #model(s6.duration.val, s6.mu.val, s6.omega.val, SM)
    #ACCURACY = 10

    #стыковка #

    #ACCURACY = 0.02
    #model(s7.duration.val, s7.mu.val, s7.omega.val, SM)
    #model(s8.duration.val, s8.mu.val, s8.omega.val, SM)
    model_animation(2, 0, 0, SM)

    ax.clear()
    ax.grid()

    ax.plot(PLOT_DATA[:, 0], PLOT_DATA[:, 2])
    angle = np.linspace(0, 2 * np.pi, 1000)
    ax.plot(R_MOON * np.sin(angle), R_MOON * np.cos(angle))
    ax.plot((50000 + R_MOON) * np.sin(angle), (50000 + R_MOON) * np.cos(angle))
    a = -np.arctan(moon_pos(GLOBAL_TIME)[0] / moon_pos(GLOBAL_TIME)[1]) - np.pi / 2
    angle = np.linspace(a - 1000 / R_MOON, a + 1000 / R_MOON, 100)
    ax.plot(R_MOON * np.cos(angle), R_MOON * np.sin(angle))
    angle = np.linspace(0, 2 * np.pi, 100)
    ax.plot(30000*np.cos(angle) + x, 30000*np.sin(angle) + y)
    print('R: ', np.sqrt(x ** 2 + y ** 2) - R_MOON - 44269)
    print('x: ', x + 1475268)
    print('y: ', y + 1000034)


# Создадим окно с графиком
fig, ax = plt.subplots()
ax.set_aspect('equal', adjustable='box')
ax.plot(x_list, y_list)
ax.grid()
fig.subplots_adjust(left=0.07, right=0.95, top=0.95, bottom=0.5)

# Создание слайдеров
s1 = Sliders(0, 0, 18000, 4675.4237, 0, 0)  # number_y, number_x, max_time, init_time, init_omega, init_mu
s2 = Sliders(1, 0, 400, 2.6870, 0, 1)
s3 = Sliders(2, 0, 400, 14.8852, 0, 0)
s4 = Sliders(3, 0, 20000, 20000, 0, 0)
s5 = Sliders(0, 1, 5000, 2663.943, 0, 0)
s6 = Sliders(1, 1, 400, 169.4, 0, 0)
s7 = Sliders(2, 1, 4000, 4000, 0, 0)
s8 = Sliders(3, 1, 4000, 1096.875, 0, 0)

plt.show()

np.savetxt('Moon_Orbit_CMSM_fot_animation', PLOT_DATA, delimiter=',')
# x 	 v_x 	 y 	 v_y 	 mass 	 mu 	 alpha 	 omega * OMEGA_MAX      time

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import math
R_EARTH = 6375000
R_MOON = 1738000
g_EARTH = 9.81
g_MOON = 1.62
GM_EARTH = R_EARTH ** 2 * 9.81
GM_MOON = R_MOON ** 2 * 1.62
R_EARTH_MOON = 384405000
OMEGA_MOON = np.sqrt(GM_EARTH / (R_EARTH_MOON ** 3))

fig = plt.figure()
ax = plt.axes()#xlim=(-7 * 10e5, 7 * 10e5), ylim=(-7 * 10e5, 7 * 10e5))
ax.set_aspect('equal', adjustable='box')
patch = plt.Circle((0, 0), R_MOON, fc='0.75')
patch2 = plt.Circle((0, 0), R_MOON + 50000, fill=False, color='c')
#patch3 = plt.Circle((0, 0), R_MOON + 185000, fc='0.25')
line, = ax.plot([], [], lw=2)

def moon_pos(t):
    return R_EARTH_MOON * np.cos(OMEGA_MOON * t), R_EARTH_MOON * np.sin(OMEGA_MOON * t)

angle = np.linspace(0, 2 * np.pi, 1000)
ax.plot((185000 + R_EARTH) * np.sin(angle), (185000 + R_EARTH) * np.cos(angle))
ax.plot(R_EARTH * np.sin(angle), R_EARTH * np.cos(angle))

time_template = 'time = %.1fh'
time_text = ax.text(0.02, 0.02, '',fontsize=10, transform=ax.transAxes)


def init():
    angle = np.linspace(0, 2 * np.pi, 1000)

    ax.set_ylim(-R_EARTH, R_EARTH)
    ax.set_xlim(-R_EARTH, R_EARTH)

    line.set_data([], [])
 

    time_text.set_text('')

    patch2.center = (moon_pos(0)[0], moon_pos(0)[1])
    patch.center = (moon_pos(0)[0], moon_pos(0)[1])
    
    ax.add_patch(patch2)
    ax.add_patch(patch)
    

    return line, time_text, patch, patch2

def get_coord(filename):
    x_ar = np.array([])
    y_ar = np.array([])
    time = np.array([])
    arr = np.genfromtxt(filename, delimiter=',')
    for row in arr:
        x = row[0]
        y = row[2]
        t = row[8]
        x_ar = np.append(x_ar, x)
        y_ar = np.append(y_ar, y)
        time = np.append(time, t)
    return (x_ar, y_ar, time)

x, y, time = get_coord('Part 1/Earth_To_Earth_Orbit')
x_1, y_1, time_1 = get_coord('Part 1/Earth_Orbit_To_Moon_Orbit')
x = np.append(x, x_1)
y = np.append(y, y_1)
time = np.append(time, time_1)
def animate(i):
    global x, y, time 
    
    #Обычные Анимашки
    # limx = max(x[:i*20])
    # limy = max(y[:i*20])
    # lim = max(limx, limy) + 300000
    # ax.set_ylim(-lim, lim) 
    # ax.set_xlim(-lim, lim)
    
    # Прикольные анимашки
    ax.plot(moon_pos(time[:i*20])[0], moon_pos(time[:i*20])[1], 'r')
    patch2.center = (R_EARTH_MOON * np.cos(OMEGA_MOON * time[i*20]), R_EARTH_MOON * np.sin(OMEGA_MOON * time[i*20]))
    patch.center = (R_EARTH_MOON * np.cos(OMEGA_MOON * time[i*20]), R_EARTH_MOON * np.sin(OMEGA_MOON * time[i*20]))
    if time[i*20] <= 8633.7:
        ax.set_ylim(y[i*20] - 10000000, y[i*20] + 10000000) 
        ax.set_xlim(x[i*20] - 10000000, x[i*20] + 10000000)
    elif time[i*20] <= 197544.2:
        ax.set_ylim(-3*R_EARTH,R_EARTH_MOON + R_MOON + 10000000) 
        ax.set_xlim(-3*R_EARTH,R_EARTH_MOON + R_MOON + 10000000)  
    else:
        ax.set_ylim(y[i*20] - 10000000, y[i*20] + 10000000) 
        ax.set_xlim(x[i*20] - 10000000, x[i*20] + 10000000)
    ax.set_aspect('equal', adjustable='box')
    ax.figure.canvas.draw()
    
    #print((R_MOON + 50000) * np.cos(angle)[:i]  + moon_pos(time[:i])[0])
    
    line.set_data(x[:i*20], y[:i*20])
    #ax.plot(x[:i*20], y[:i*20], 'b')
    #ax.plot(x[i*20], y[i*20], 'ro')
    #print(i)
    time_text.set_text(time_template % (time[i*20]/3600))
    return line, time_text, patch, patch2

anim = animation.FuncAnimation(fig, animate, init_func=init,
                                frames=math.floor(len(x)/20), interval=1, repeat=False, blit=True)

#anim.save('To_Earth_Orbit.gif', writer='imagemagick')
plt.show()
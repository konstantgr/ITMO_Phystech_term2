import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import math
import copy

R_EARTH = 6375000
R_MOON = 1738000
g_EARTH = 9.81
g_MOON = 1.62
GM_EARTH = R_EARTH ** 2 * 9.81
GM_MOON = R_MOON ** 2 * 1.62
R_EARTH_MOON = 384405000
OMEGA_MOON = np.sqrt(GM_EARTH / (R_EARTH_MOON ** 3))

fig = plt.figure()
ax = plt.axes()
ax.set_aspect('equal', adjustable='box')
patch = plt.Circle((0, 0), R_MOON, fc='0.75')
patch2 = plt.Circle((0, 0), 30000, color='r')
line, = ax.plot([], [], lw=2)
line2, = ax.plot([], [], lw=2)

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
    line2.set_data([], [])
    
    time_text.set_text('')

    patch2.center = (0, 0)
    patch.center = (0, 0)
    
    ax.add_patch(patch2)
    ax.add_patch(patch)
    
    return line, line2, time_text, patch, patch2

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


x, y, time = get_coord('Part 2/Moon_Orbit_To_Moon')
x_2, y_2, time_2 = get_coord('Part 2/Moon_To_Moon_Orbit')
x_cmsm, y_cmsm, time_cmsm = get_coord('Part 2/Moon_Orbit_CMSM')

x = np.append(x, x_2)
y = np.append(y, y_2)
time = np.append(time, time_2)



def animate(i):
    global x, y, time
   
    # анимашки
    patch2.center = (x[i*20], y[i*20])
    patch.center = (0, 0)
    ax.set_ylim(-R_MOON - 1000000, R_MOON + 1000000) 
    ax.set_xlim(-R_MOON - 1000000, R_MOON + 1000000)
    
    ax.set_aspect('equal', adjustable='box')
    ax.figure.canvas.draw()
    #line.set_data(x_cmsm[:i*3], y_cmsm[:i*3])
    line2.set_data(x[:i*20], y[:i*20])
    
   
    time_text.set_text(time_template % (time[i*3]/3600))

    return line, line2, time_text, patch, patch2

anim = animation.FuncAnimation(fig, animate, init_func=init,
                                frames=math.floor(max(len(x)/20, len(x_cmsm)/20)), interval=1, repeat=False, blit=True)

#anim.save('From_Moon_To_Moon_Orbit.gif', writer='imagemagick')
plt.show()
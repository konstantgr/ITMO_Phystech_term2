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

fig = plt.figure(figsize=(7,7))
#plt.axis('off')
plt.gca().xaxis.set_major_locator(plt.NullLocator())
plt.gca().yaxis.set_major_locator(plt.NullLocator())

ax = plt.axes()#xlim=(-7 * 10e5, 7 * 10e5), ylim=(-7 * 10e5, 7 * 10e5))
ax.set_aspect('equal', adjustable='box')
patch = plt.Circle((0, 0), R_MOON, fc='0.75')
patch2 = plt.Circle((0, 0), R_MOON + 50000, fill=False, color='c')
patch3 = plt.Circle((0, 0), R_EARTH, color='#99ffcc')
#patch3 = plt.Circle((0, 0), R_MOON + 185000, fc='0.25')
line, = ax.plot([], [], lw=2)
line2, = ax.plot([], [], lw=2)
def moon_pos(t):
    return R_EARTH_MOON * np.cos(OMEGA_MOON * t), R_EARTH_MOON * np.sin(OMEGA_MOON * t)

angle = np.linspace(0, 2 * np.pi, 1000)
ax.plot((200000 + R_EARTH) * np.sin(angle), (200000 + R_EARTH) * np.cos(angle), color='0.8')
ax.plot(R_EARTH * np.sin(angle), R_EARTH * np.cos(angle))

time_template = 'time = %.1fh'
time_text = ax.text(0.02, 0.95, '',fontsize=10, transform=ax.transAxes)


def init():
    angle = np.linspace(0, 2 * np.pi, 1000)

    ax.set_ylim(-R_EARTH, R_EARTH)
    ax.set_xlim(-R_EARTH, R_EARTH)

    line.set_data([], [])
    line2.set_data([], [])
    
    time_text.set_text('')

    patch3.center = (0,0)
    patch2.center = (moon_pos(0)[0], moon_pos(0)[1])
    patch.center = (moon_pos(0)[0], moon_pos(0)[1])
    
    ax.add_patch(patch2)
    ax.add_patch(patch)
    ax.add_patch(patch3)
    

    return line, line2, time_text, patch, patch2, patch3

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


def dif_coord(x, y, t):
    for i in range(len(t)):
        x[i] += moon_pos(t[i])[0]
        y[i] += moon_pos(t[i])[1]
    return x, y

x, y, time = get_coord('Part 1/Earth_To_Earth_Orbit')
x_1, y_1, time_1 = get_coord('Part 1/Earth_Orbit_To_Moon_Orbit')
x_2, y_2, time_2 = get_coord('Part 2/Moon_Orbit_To_Moon')
x_3, y_3, time_3 = get_coord('Part 2/Moon_To_Moon_Orbit')
x_4, y_4, time_4 = get_coord('Part 3/Moon_Orbit_To_Earth_Orbit')
x_5, y_5, time_5 = get_coord('Part 3/Earth_Orbit_To_Earth')

x_cmsm, y_cmsm, time_cmsm = get_coord('Part 2/Moon_Orbit_CMSM')
print(time_2[0])
x = np.append(x, x_1)
y = np.append(y, y_1)
x_copy = copy.copy(x)
y_copy = copy.copy(y)


x_2, y_2 = dif_coord(x_2, y_2, time_2)
x_3, y_3 = dif_coord(x_3, y_3, time_3)
x_cmsm, y_cmsm = dif_coord(x_cmsm, y_cmsm, time_cmsm)

x_copy = np.append(x_copy, x_cmsm)
y_copy = np.append(y_copy, y_cmsm)

x = np.append(x, x_2)
y = np.append(y, y_2)

x = np.append(x, x_3)
y = np.append(y, y_3)

x = np.append(x, x_4)
y = np.append(y, y_4)

x = np.append(x, x_5)
y = np.append(y, y_5)


time = np.append(time, time_1)
time_copy = copy.copy(time)

time = np.append(time, time_2)

time = np.append(time, time_3)
time = np.append(time, time_4)
time = np.append(time, time_5)


time_copy = np.append(time_copy, time_cmsm)

# ax.plot(x, y)
# plt.show()
# fig.savefig('trajectory.png')

# for i in range(len(time)):
#     time[i] = int(time[i])   
# #time = int(time)
# print(time)
# print(time_cmsm)


def animate(i):
    global x, y, time, x_copy, y_copy, time_copy
    #Обычные Анимашки
    # limx = max(x[:i*20])
    # limy = max(y[:i*20])
    # lim = max(limx, limy) + 300000
    # ax.set_ylim(-lim, lim) 
    # ax.set_xlim(-lim, lim)
    # Прикольные анимашки
    ax.plot(moon_pos(time[:i * 20])[0], moon_pos(time[:i * 20])[1], 'r')
    patch2.center = (R_EARTH_MOON * np.cos(OMEGA_MOON * time[i*20]), R_EARTH_MOON * np.sin(OMEGA_MOON * time[i*20]))
    patch.center = (R_EARTH_MOON * np.cos(OMEGA_MOON * time[i*20]), R_EARTH_MOON * np.sin(OMEGA_MOON * time[i*20]))
    #patch3.center = (0, 0)
    if time[i*20] <= 1303.7:
        ax.set_ylim(y[i*20] - 100000, y[i*20] + 100000) 
        ax.set_xlim(x[i*20] - 100000, x[i*20] + 100000)
    elif time[i*20] <= 8633.7: # Полет до вылета с земли
        ax.set_ylim(y[i*20] - 10000000, y[i*20] + 10000000) 
        ax.set_xlim(x[i*20] - 10000000, x[i*20] + 10000000)
    elif time[i*20] <= 197544.2: # Полет до Луны далекий план
        ax.set_ylim(-3*R_EARTH,R_EARTH_MOON + R_MOON + 10000000) 
        ax.set_xlim(-3*R_EARTH,R_EARTH_MOON + R_MOON + 10000000)  
    elif time[i*20] <= 274831.0: # Полет до Луны близкий план до отстыковки
        #line2.set_data(x_copy[:i*20], y_copy[:i*20])
        ax.set_ylim(y[i*20] - 10000000, y[i*20] + 10000000) 
        ax.set_xlim(x[i*20] - 10000000, x[i*20] + 10000000)
    elif time[i*20] <= 296200.9072034865:
        #time.
        ax.set_ylim(y[i*20] - 100000, y[i*20] + 100000) 
        ax.set_xlim(x[i*20] - 100000, x[i*20] + 100000)
    elif time[i*20] <= 304025.9072034865:        
        #print(list(time_cmsm).index(int(time[i*20])))
        ax.set_ylim(y[i*20] - 10000000, y[i*20] + 10000000) 
        ax.set_xlim(x[i*20] - 10000000, x[i*20] + 10000000)
    elif time[i*20] < 140.7 * 3600: # Полет до Луны далекий план
        ax.set_ylim(-3*R_EARTH,R_EARTH_MOON + R_MOON + 10000000) 
        ax.set_xlim(-3*R_EARTH,R_EARTH_MOON + R_MOON + 10000000)  
    elif time[i*20] < 141.4 * 3600:
        ax.set_ylim(y[i*20] - 1000000, y[i*20] + 1000000) 
        ax.set_xlim(x[i*20] - 1000000, x[i*20] + 1000000)
    else:
        ax.set_ylim(y[i*20] - 100000, y[i*20] + 100000) 
        ax.set_xlim(x[i*20] - 100000, x[i*20] + 100000)
    ax.set_aspect('equal', adjustable='box')
    ax.figure.canvas.draw()
    
    #print((R_MOON + 50000) * np.cos(angle)[:i]  + moon_pos(time[:i])[0])
    
    line.set_data(x[:i*20], y[:i*20])
    #ax.plot(x[:i*20], y[:i*20], 'b')
    #ax.plot(x[i*20], y[i*20], 'ro')
    #print(i)
    time_text.set_text(time_template % (time[i*20]/3600))
    return line, line2, time_text, patch, patch2, patch3

anim = animation.FuncAnimation(fig, animate, init_func=init, frames=math.floor(len(x)/20), interval=1, repeat=False, blit=True)
anim.save('To_Earth_Orbit.gif', writer='imagemagick')
print(1)

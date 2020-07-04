import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
R_EARTH = 6375000
fig = plt.figure()
ax = plt.axes()#xlim=(-7 * 10e5, 7 * 10e5), ylim=(-7 * 10e5, 7 * 10e5))
ax.set_aspect('equal', adjustable='box')

line, = ax.plot([], [], lw=2)

angle = np.linspace(0, 2 * np.pi, 1000)
ax.plot((185000 + R_EARTH) * np.sin(angle), (185000 + R_EARTH) * np.cos(angle))
ax.plot(R_EARTH * np.sin(angle), R_EARTH * np.cos(angle))

time_template = 'time = %.1fh'
time_text = ax.text(0.02, 0.02, '',fontsize=10, transform=ax.transAxes)

def init():
    ax.set_ylim(-R_EARTH, R_EARTH)
    ax.set_xlim(-R_EARTH, R_EARTH)
    line.set_data([], [])
    time_text.set_text('')
    return line, time_text

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
x_1, y_1, time_1 = get_coord('Earth_Orbit_To_Moon_Orbit')
x = np.append(x, x_1)
y = np.append(y, y_1)
time = np.append(time, time_1)
def animate(i):
    global x, y, time 
    
    #Обычные Анимашки
    limx = max(x[:i*20])
    limy = max(y[:i*20])
    lim = max(limx, limy) + 300000
    ax.set_ylim(-lim, lim) 
    ax.set_xlim(-lim, lim)
    
    # Прикольные анимашки
    # ax.set_ylim(y[i*20] - 10000000, y[i*20] + 10000000) 
    # ax.set_xlim(x[i*20] - 10000000, x[i*20] + 10000000)
    
    ax.figure.canvas.draw()
    #ax.set_aspect('equal', adjustable='box')
 
    line.set_data(x[:i*20], y[:i*20])
    #ax.plot(x[:i*20], y[:i*20], 'b')
    #ax.plot(x[i*20], y[i*20], 'ro')
    print(i)
    time_text.set_text(time_template % (time[i*18]/3600))
    return line, time_text

anim = animation.FuncAnimation(fig, animate, init_func=init,
                                frames=int(len(x) / 20) - 10, interval=1, repeat=False, blit=True)

#anim.save('To_Earth_Orbit.gif', writer='imagemagick')
plt.show()
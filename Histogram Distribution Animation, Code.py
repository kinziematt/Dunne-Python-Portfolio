import matplotlib.pyplot as plt
import numpy as np

import matplotlib.animation as animation

n = 100
x1 = np.random.normal(-2.5, 1, 10000)
x2 = np.random.gamma(2, 1.5, 10000)
x3 = np.random.exponential(2, 10000)+7
x4 = np.random.uniform(14,20, 10000)

def update(curr):
    # check if animation is at the last frame, and if so, stop the animation a
    if curr == n: 
        a.event_source.stop()
    plt.cla()
    plt.hist(x1[:curr], normed=True, bins=20, alpha=0.5)
    plt.hist(x2[:curr], normed=True, bins=20, alpha=0.5)
    plt.hist(x3[:curr], normed=True, bins=20, alpha=0.5)
    plt.hist(x4[:curr], normed=True, bins=20, alpha=0.5)
    plt.axis([-7,21,0,0.6])
    plt.text(x1.mean()-1.5, 0.5, 'x1\nNormal')
    plt.text(x2.mean()-1.5, 0.5, 'x2\nGamma')
    plt.text(x3.mean()-1.5, 0.5, 'x3\nExponential')
    plt.text(x4.mean()-1.5, 0.5, 'x4\nUniform')
fig = plt.figure()
a = animation.FuncAnimation(fig, update, interval=10)
#mywriter = animation.FFMpegWriter()
#a.save('multi_plot_distributions.mp4', writer=mywriter, fps=30)
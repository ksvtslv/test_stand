
import numpy as np
import matplotlib.pyplot as plt

n = 10
# time vector
#t = np.linspace(0, 1, n, endpoint=True)
t = np.linspace(0, np.pi/2, n, endpoint=True)
# sine wave
#x = np.sin(np.pi*t) + np.sin(2*np.pi*t) + np.sin(3*np.pi*t) + np.sin(5*np.pi*t)
x = np.sin(t)
plt.plot(t, x)
plt.show()



# Select: plot, stem, bar
#def plt_sel(s, *args, **kwargs):
#    if s == 0:
#        return plt.plot(*args)
#    if s == 1:
#        return plt.stem(*args, **kwargs)
#    if s == 2:
#        return plt.step(*args)
#
## Subplot titles
#t_titles = ['Аналоговый', 'Дискретный', 'Квантованный']
#
## Plot figures
#fig = plt.figure(figsize=(16, 4), dpi=80)
#for i in range(3):
#    plt.subplot(1, 3, i+1)
#    plt.title(t_titles[i]) 
#    plt_sel(i, t, x)
#    plt.xlim([0, 1])
#    plt.yticks(np.linspace(np.floor(np.min(x)), np.ceil(np.max(x)), 9))
#    plt.grid(True)
#    
#    # change plot view
#    ax = plt.gca()
#    ax.spines['right'].set_color('none')
#    ax.spines['top'].set_color('none')
#    ax.spines['bottom'].set_position(('data',0))
#plt.tight_layout()
#plt.show()
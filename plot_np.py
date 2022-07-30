import matplotlib.pyplot as plt
import numpy as np
from sklearn import preprocessing
from scipy.ndimage.filters import gaussian_filter, gaussian_laplace, gaussian_filter1d, gaussian_gradient_magnitude
path = 'C:/Users/user/Desktop/Podometr'
a = np.load(path + '/1.npy')
a[0] = np.rot90(a[0],k=3)
fig = plt.figure(figsize=(10, 8))
normal_a = a[0]
normal_a = gaussian_filter(normal_a, sigma=(0.7,0.7), mode='reflect')
max_a = np.amax(normal_a)
min_a = np.amin(normal_a)
print(max_a , min_a)
for i in range(0,len(normal_a[0])):
    for j in range(0,len(normal_a[0])):
        normal_a[i][j] = 3*(normal_a[i][j]-min_a)/(max_a - min_a)
        print(normal_a[i][j])
x,y = range(len(a[0])),range(len(a[0]))
xgrid, ygrid = np.meshgrid(x, y)
axes_2 = fig.add_subplot(2, 2, 1, projection='3d')
axes_1 = fig.add_subplot(2, 2, 2)
axes_2.plot_surface(xgrid, ygrid, normal_a)
axes_2.set_title('Моя нормализации')
axes_1.imshow(normal_a, extent=([0, 32, 0, 32]), cmap='Blues', interpolation='none', vmin=0, vmax=np.amax(normal_a))
axes_1.set_title('Моя нормализации')
min_max_scaler = preprocessing.MinMaxScaler(feature_range=(0, 3))
a[0] = min_max_scaler.fit_transform(a[0])
axes_4 = fig.add_subplot(2, 2, 3, projection='3d')
axes_3 = fig.add_subplot(2, 2, 4)
axes_4.plot_surface(xgrid, ygrid, a[0])
axes_3.imshow(a[0], extent=([0, 32, 0, 32]), cmap='Blues', interpolation='none', vmin=0, vmax=3)
axes_3.set_title('Нормализации sklearn')
axes_4.set_title('Нормализации sklearn')
import numpy2stl
fn='test.stl'
numpy2stl.numpy2stl(normal_a, fn, solid=True)
plt.show()




"""import scipy as sp
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
x = [614, 763, 850]
y = [720, 1220, 5220]
plt.scatter(x, y)"""
"""fx = sp.linspace(x[0], x[-1], 1000)
for d in range(2, 3):
    # получаем параметры модели для полинома степени d
    fp, residuals, rank, sv, rcond = sp.polyfit(x, y, d, full=True)
    print("Параметры модели: %s" % fp)
    # функция-полином, если её напечатать, то увидите математическое выражение
    f = sp.poly1d(fp)
    plt.plot(fx, f(fx), linewidth=2)
    #print(f)
plt.show()"""

"""fx = np.linspace(x[-1], x[0] + 1, 1000)
legend = []
legend.append('Данные прибора')
for d in range(2, 3):
    fp = np.polyfit(x, y, d)
    f = np.poly1d(fp)
    print(f)
    plt.plot(fx, f(fx), linewidth=4)
    txt = str(d) + "- го порядка"
    #legend.append(txt)
    #legend.append("")
#plt.legend(legend, loc="upper right",fontsize=20)
plt.grid()
plt.show()"""
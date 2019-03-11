from scipy.io import wavfile
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
import pylab

fs, data = wavfile.read('./audios_imagenes_prueba/negro.wav')

t = np.arange(len(data))/fs

signal = scipy.signal.hilbert(data) #dejar data en cuadratura para sacarle angulo
inst_ph = np.unwrap(np.angle(signal)) #unwrap deja a la fase de forma lineal en vez de rampa
inst_fr = (np.diff(inst_ph) / (2.0*np.pi) * fs) #diff toma el valor de x(n+1) y lo resta con x(n)

fig = plt.figure()
ax0 = plt.subplot(211)
ax0.plot(t[1:], inst_fr) #gracias a np.diff
ax1 = plt.subplot(212)
ax1.plot(t, inst_ph)
pylab.show()

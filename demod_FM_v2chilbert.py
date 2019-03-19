from scipy.io import wavfile
#import soundfile as sf
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
import pylab
import math
from funcion_tincho import escribir_pixel
from PIL import Image
import collections

def lowpass(cutout, delta_w, atten):
    '''
    cutout y delta_w en fracciones de pi radianes por segundo.

    atten en decibeles positivos.
    '''

    beta = 0
    if atten > 50:
        beta = 0.1102 * (atten - 8.7)
    elif atten < 21:
        beta = 0
    else:
        beta = 0.5842 * (atten - 21)**0.4 + 0.07886 * (atten - 21)

    length = math.ceil((atten - 8) / (2.285 * delta_w * math.pi)) + 1;
    if length % 2 == 0:
        length += 1

    coeffs = np.kaiser(length, beta)

    # i es el indice en el vector, n es el eje con el cero centrado en el medio
    # del filtro
    for i, n in enumerate(range(
            int(-(length - 1) / 2),
            int((length - 1) / 2)+1)):

        if n == 0:
            coeffs[i] *= cutout
        else:
            coeffs[i] *= math.sin(n * math.pi * cutout) / (n * math.pi)

    return coeffs

def filtrar(input, cutout, delta_w, atten):
    '''
    La derecha del buff tiene la muestra mas reciente y tiene el indice mas alto
    '''

    coeffs = lowpass(cutout, delta_w, atten)

    #  plot(coeffs, numpy.abs(numpy.fft.fft(coeffs)))

    buf = collections.deque([0] * len(coeffs))

    for s in input:
        buf.popleft()
        buf.append(s)
        sum = 0
        for j in range(len(coeffs)):
            sum += buf[-j - 1] * coeffs[j]

        yield sum

fs, data = wavfile.read('./audios_imagenes_prueba/pass_1_norm_7000.wav')
img = Image.new('YCbCr',(640,496),"white")

ts = 1/fs
window = np.kaiser(55,3.3953) #kaiser calculado con fs = 48000
filter = []
for n in range((-55+1)//2,(55-1)//2+1):
    if n % 2 != 0:
        filter.append(2/(np.pi*n))
    else:
        filter.append(0)
hilbert = filter * window

zeros = np.zeros(27)
datareal = np.concatenate([zeros,data,zeros])
datacompleja = np.convolve(data,hilbert)*1j

t = np.arange(len(data))/fs
signal = datareal + datacompleja  #dejar data en cuadratura para sacarle angulo
inst_ph = np.unwrap(np.angle(signal)) #unwrap deja a la fase de forma lineal en vez de rampa
inst_fr = (np.diff(inst_ph) / (2.0*np.pi) * fs) #diff toma el valor de x(n+1) y lo resta con x(n)



inst_fr = list(filtrar(inst_fr, 0.3, 0.2, 20))

fig = plt.figure()
ax0 = plt.subplot(211)
ax0.plot(range(len(inst_fr)),inst_fr)
ax1 = plt.subplot(212)
ax1.plot(range(len(inst_fr)),np.abs(np.fft.fft(inst_fr)))

pylab.show()

muestras = 0
cont_linea = -1
i = 0


while i < len(inst_fr):

    if 900 <= inst_fr[i] <= 1300:
        muestras += 1 #contador de muestras, si muchas se encuentran en el rango era cambio de linea
    if muestras > int(0.018*fs):
        cont_linea += 2 #casi seguro indico la siguiente
        muestras = 0 #resetear muestras para la proxima iteracion
        columna = 0
        i = i-int(0.018*fs)+int((0.02+0.002080)*fs)

        try:

            y_resampleados = scipy.signal.resample(inst_fr[i:i+int(0.1216*fs)],640)
            for columna,valor in enumerate(y_resampleados):
                if valor < 1500:
                    escribir_pixel(img, columna, cont_linea, "lum", 1500)
                elif valor > 2300:
                    escribir_pixel(img, columna, cont_linea, "lum", 2300)
                else:
                    escribir_pixel(img, columna, cont_linea, "lum", valor)

            cr_resampleados = scipy.signal.resample(inst_fr[i+int(0.1216*fs):i+int(0.1216*2*fs)],640)
            for columna,valor in enumerate(cr_resampleados):
                if valor < 1500:
                    escribir_pixel(img, columna, cont_linea, "cr", 1500)
                elif valor > 2300:
                    escribir_pixel(img, columna, cont_linea, "cr", 2300)
                else:
                    escribir_pixel(img, columna, cont_linea, "cr", valor)

            cb_resampleados = scipy.signal.resample(inst_fr[i+int(0.1216*2*fs):i+int(0.1216*3*fs)],640)
            for columna,valor in enumerate(cb_resampleados):
                if valor < 1500:
                    escribir_pixel(img, columna, cont_linea, "cb", 1500)
                elif valor > 2300:
                    escribir_pixel(img, columna, cont_linea, "cb", 2300)
                else:
                    escribir_pixel(img, columna, cont_linea, "cb", valor)


            ny_resampleados = scipy.signal.resample(inst_fr[i+int(0.1216*3*fs):i+int(0.1216*4*fs)],640)
            for columna,valor in enumerate(ny_resampleados):
                if valor < 1500:
                    escribir_pixel(img, columna, cont_linea, "nxt_lum", 1500)
                elif valor > 2300:
                    escribir_pixel(img, columna, cont_linea, "nxt_lum", 2300)
                else:
                    escribir_pixel(img, columna, cont_linea, "nxt_lum", valor)
        except:
            break




        i+=int(0.1216*2*fs)

    i += 1

imgrgb = img.convert("RGB")
imgrgb.save("./imagenprueba.png","PNG")


#ax1 = plt.subplot(212)
#ax1.plot(t[i+5600*3+1:i+5400*4+1],inst_fr[i+5600*3:i+5400*4])
#pylab.show()
#break

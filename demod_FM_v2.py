from scipy.io import wavfile
#import soundfile as sf
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
import pylab
from funcion_tincho import escribir_pixel
from PIL import Image


fs, data_int = wavfile.read('./audios_imagenes_prueba/pruebaestrella.wav')
img = Image.new('YCbCr',(640,496),"white")

data = []

for d in data_int:
    data.append(float(d))


ts = 1/fs
t = np.arange(len(data))/fs
signal = scipy.signal.hilbert(data) #dejar data en cuadratura para sacarle angulo
inst_ph = np.unwrap(np.angle(signal)) #unwrap deja a la fase de forma lineal en vez de rampa
inst_fr = (np.diff(inst_ph) / (2.0*np.pi) * fs) #diff toma el valor de x(n+1) y lo resta con x(n)

muestras = 0
cont_linea = -1
i = 0

while i < len(inst_fr):

    if 1100 <= inst_fr[i] <= 1300:
        muestras += 1 #contador de muestras, si muchas se encuentran en el rango era cambio de linea
    if muestras > int(0.0198*fs):
        cont_linea += 2 #casi seguro indico la siguiente
        muestras = 0 #resetear muestras para la proxima iteracion
        columna = 0

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




        i+=1000

    i += 1

#fig = plt.figure()
#ax0 = plt.subplot(211)
#ax0.plot(range(len(ny_resampleados)), ny_resampleados)
#ax1 = plt.subplot(212)
#ax1.plot(t[i+5600*3+1:i+5400*4+1],inst_fr[i+5600*3:i+5400*4])
#pylab.show()
#break
imgrgb = img.convert("RGB")
imgrgb.save("./imagenprueba.png","PNG")

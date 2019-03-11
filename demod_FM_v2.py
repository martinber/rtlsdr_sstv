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


muestras = 0
cont_linea = -1

i = 20000
while i < len(inst_fr):

    if 1150 <= inst_fr[i] <= 1250:
        muestras += 1 #contador de muestras, si muchas se encuentran en el rango era cambio de linea
    if muestras > 800:
        cont_linea += 2 #casi seguro indico la siguiente
        muestras = 0 #resetear muestras para la proxima iteracion
        columna = 0
        espacio_muestra = 0
        salida = []

        y_resampleados = np.linspace(inst_fr[i],inst_fr[i+5360],640)
        for columna,valor in enumerate(y_resampleados):
            imagen.escribir_pixel(columna, cont_linea, "lum", valor)

        cb_resampleados = np.linspace(inst_fr[i*2],inst_fr[i+5360*2],640)
        for columna,valor in enumerate(cb_resampleados):
            imagen.escribir_pixel(columna, cont_linea, "cb", valor)

        cr_resampleados = np.linspace(inst_fr[i*3],inst_fr[i+5360*3],640)
        for columna,valor in enumerate(cr_resampleados):
            imagen.escribir_pixel(columna, cont_linea, "cr", valor)

        ny_resampleados = np.linspace(inst_fr[i*4],inst_fr[i+5360*4],640)
        for columna,valor in enumerate(ny_resampleados):
            imagen.escribir_pixel(columna, cont_linea, "nxt_lum", valor)




        i+=5000

    i += 1

print(cont_linea)

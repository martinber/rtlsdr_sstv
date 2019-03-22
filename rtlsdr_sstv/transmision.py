from PIL import Image
import wave, math, struct
import matplotlib.pyplot as plt
import pylab
from resizeimage import resizeimage
import sys
import numpy as np
from scipy.io import wavfile
import dsp
import raw_file

def audiogen(filenamein,frec_sample,wavnameout):
	imagen = Image.open(filename) #importa la imagen introduciendo el path hacia la misma
	im_re = imagen.resize((640,496), Image.BICUBIC) #reacomoda la imagen para que quede del tamaño deseado
	imagen2 = im_re.convert('YCbCr') #Transformacion al formato deseado para la transmision

	ancho = imagen2.width
	alto  = imagen2.height

	frec_negro = 1500
	frec_blanco = 2300
	rango = frec_blanco - frec_negro

	tiempo = 120 #segundos, es la duración que de la imagen en modo PD120
	cant_valores = alto * ancho * 3 #cantidad de valores contando la intesidad, intensidad menos azul e intensidad menos rojo
	duracion = 190*(10**-6) #la duración de cada uno de los valores del pixel en microsegundos
	max_valor = 255 #determinado por (2^8)-1  tamaño de un byte porque es lo que escribe en el audio

	filas = []

	#fs = frec_sample
	ts = 1/frec_sample

	fsinc = 1200 #frecuencia y tiempo de sincronización, que se envía al principio de cada línea de píxeles
	tsinc = 0.02
	fpor = 1500 # frecuencia y tiempo, que se envía luego de la de sincronización
	tpor = 0.00208

	for i in range(alto) :

		fila = []
		for j in range(ancho) :
			fila.append(imagen2.getpixel((j,i))) #se obtienen los píxeles de la imagen

	filas.append(fila)

	frec = []

	for j in range(0,alto,2) : #determina el vector que contiene cada una de las frecuencias de los píxeles
		frec.append((fsinc, tsinc))
		frec.append((fpor, tpor))
		for i in range(ancho) :
			frec.append((conv_frec(filas[j][i][0]), duracion)) #valores de intensidad "Y"
		for i in range(ancho) :
			val = ((conv_frec(filas[j][i][2]))+(conv_frec(filas[j+1][i][2])))/2 #promedio de las dos líneas de Cb debido al código
			frec.append((val, duracion))
		for i in range(ancho) :
			val = ((conv_frec(filas[j][i][1]))+(conv_frec(filas[j+1][i][1])))/2 #promedio de las dos líneas de Cr debido al código
			frec.append((val , duracion))
		for i in range(ancho) :
			frec.append((conv_frec(filas[j+1][i][0]), duracion)) #proxima linea de intensidad "Y"

	audio = wave.open(wavnameout,"wb")
	audio.setnchannels(1) # mono
	audio.setsampwidth(2) #2 bytes
	audio.setframerate(fs) #frecuencia de muestreo
	datos = 0
	muestras = 0
	offset = 0
	for i, s in frec :
		muestras += s * fs
		x = int(muestras)

		for k in range(x) :

			datos = int(32767.0*math.sin((2*math.pi*float(k)*i*float(ts))+offset)) #valores que va tomando el seno, para generar la señal de audio
			data = struct.pack('<h', datos)
			audio.writeframesraw( data )

		offset += 2*math.pi*ts*(k+1)*i #valor de comienzo de la próxima iteración
		muestras -= x

	audio.writeframes(b'')
	audio.close()
	return audio

def conv_frec (valor_pixel) :

	frec_negro = 1500
	frec_blanco = 2300
	rango = frec_blanco - frec_negro
	max_valor = 255

	valor = int(frec_negro + valor_pixel * rango/max_valor) #calcula la frecuencia que tiene cada valor de cada pixel

	return valor

#def señal_modulada(audio,frec_carrier):

#	frec_sample_audio, data = wavfile.read("arcoiris.wav")

#	fc= 50000
#	fs_sdr= 4*fc

def agregar_ceros(datos_audio, fs_audio, fs_sdr) :

	ceros = int(fs_sdr/frec_audio)-1
	vector_datos = []

	for i in vector_data:
	    vector_datos.append(i)
	    for i in range(ceros):
	        vector_datos.append(0)

	return vector_datos

def filtrar(ceros, datos) :

	vector_datos = []
	filtro = dsp.lowpass(1/(ceros+1),0.1,30)

	vector_datos = np.convolve(datos,filtro,'full')

	return vector_datos

def generadora_raw (vector_datos, fs_sdr, fc) :

	with open("gqrx_20190319_030431_101324000_{}_fc.raw".format(int(fs)), "wb") as f:
	    for i in range(len(vector_final)) :
	        sample = 0.5*np.exp(1j*(2*math.pi*fc*i/fs_sdr+5*(vector_datos[i])))

	        raw_file.write_complex_sample(f, sample)

def main(args):

	
    print(args)

    # Codigo para transmision

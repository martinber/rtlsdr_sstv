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
import SoapySDR
from SoapySDR import * #SOAPY_SDR_ constants

import sdr

def audiogen(filename, audio_rate, wavnameout):
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
	ts = 1/audio_rate

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
	audio.setframerate(audio_rate) #frecuencia de muestreo
	datos = 0
	muestras = 0
	offset = 0
	for i, s in frec :
		muestras += s * audio_rate
		x = int(muestras)

		for k in range(x) :

			datos = int(32767.0*math.sin((2*math.pi*float(k)*i*float(ts))+offset)) #valores que va tomando el seno, para generar la señal de audio
			data = struct.pack('<h', datos)
			audio.writeframesraw( data )

		offset += 2*math.pi*ts*(k+1)*i #valor de comienzo de la próxima iteración
		muestras -= x

	audio.writeframes(b'')
	audio.close()
	#return audio

def conv_frec (valor_pixel) :

	frec_negro = 1500
	frec_blanco = 2300
	rango = frec_blanco - frec_negro
	max_valor = 255

	valor = int(frec_negro + valor_pixel * rango/max_valor) #calcula la frecuencia que tiene cada valor de cada pixel

	return valor


def agregar_ceros(datos_audio, fs_audio, fs_sdr) :

	data = []

	for i in (datos_audio) :
	    data.append(i/32767)

	ceros = int(fs_sdr/fs_audio)-1
	vector_datos = []

	for i in data:
	    vector_datos.append(i)
	    for i in range(ceros):
	        vector_datos.append(0)

	return vector_datos, ceros

def filtrar(ceros, datos) :

	vector_datos = []
	filtro = dsp.lowpass(1/(ceros+1),0.1,30)

	vector_datos = np.convolve(datos,filtro,'full')

	return vector_datos

def generadora_raw (vector_datos, fs_sdr) :

	fc = 10000
	with open("gqrx_20190319_030431_101324000_{}_fc.raw".format(int(fs_sdr)), "wb") as f:
	    for i in range(len(vector_datos)) :
	        sample = 0.5*np.exp(1j*(2*math.pi*fc*i/fs_sdr+5*(vector_datos[i])))

	        raw_file.write_complex_sample(f, sample)


def main(args):
	#args.image #contiene el nombre de archivo de la imagen
	#args.audio_rate
	#args.rf_rate #tasa de muestreo del sdr
	#args.rf_freq
	if not args.from_tmp_raw :
		audiogen(args.image, args.audio_rate, "audio.wav")

		fs_audio, data = wavfile.read("audio.wav")

		señal_interpolada, ceros = agregar_ceros(data, fs_audio, args.rf_rate)

		señal_filtrada = filtrar(ceros, señal_interpolada)

		generadora_raw(señal_filtrada, args.rf_rate)



	sdr.siggen_app(
		args=args.soapy_args,
		rate=args.rf_rate,
		freq=args.rf_freq,
		tx_ant=args.rf_ant,
		tx_gain=args.rf_gain,
	)
    # Codigo para transmision

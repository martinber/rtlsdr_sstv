from PIL import Image
import wave, math

imagen = Image.open("negro.png")
imagen2 = imagen.convert('YCbCr')

ancho = imagen2.width
alto  = imagen2.height

frec_negro = 1500
frec_blanco = 2300
rango = frec_blanco - frec_negro

tiempo = 120 #segundos
cant_valores = alto * ancho * 3 #cantidad de valores contando la intesidad, intensidad menos azul e intensidad menos rojo
duracion = tiempo / cant_valores #la duración de cada uno de los valores del pixel en segundos

max_valor = 255

filas = []

fs = 44100
ts = 1/fs

for i in range(alto) :

	fila = []
	for j in range(ancho) :
		#print(i,j)
		fila.append(imagen2.getpixel((j,i)))


	filas.append(fila)

def conv_frec (valor_pixel) :
	valor = int(frec_negro + valor_pixel * rango/max_valor)
	
	return valor

frec = []
for j in range(alto) :
	for i in range(ancho) : 
		frec.append(conv_frec(filas[j][i][0]))
	for i in range(ancho) :
		frec.append(conv_frec(filas[j][i][1]))
	for i in range(ancho) :
		frec.append(conv_frec(filas[j][i][2]))

datos = []
muestras = int(duracion * fs)
offset = 0
for i in range(len(frec)) :
	for t in range(muestras):
		datos.append(math.sin((2*math.pi*t*frec[i]*ts)+offset))
	offset += duracion

audio = wave.open("audio.wav","wb")
num_canales = 1
bytes = 1
total_muestras = len(frec)
comptype = "NONE"
compname = "not compressed"

audio.setparams((num_canales,bytes,fs,total_muestras,comptype,compname))
#print(datos)
enteros = []
for v in datos:
    enteros.append(int((v*128)+128))

#print(datos)
audio.writeframes(bytearray(enteros))

audio.close()


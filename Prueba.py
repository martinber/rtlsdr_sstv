from PIL import Image
import wave, math
import matplotlib.pyplot as plt
import pylab

imagen = Image.open("./audios_imagenes_prueba/prueba.png")
imagen2 = imagen.convert('YCbCr')

ancho = imagen2.width
alto  = imagen2.height

frec_negro = 1500
frec_blanco = 2300
rango = frec_blanco - frec_negro

tiempo = 120 #segundos
cant_valores = alto * ancho * 3 #cantidad de valores contando la intesidad, intensidad menos azul e intensidad menos rojo
duracion = 190*(10**-6) #la duración de cada uno de los valores del pixel en segundos

max_valor = 255

filas = []

fs = 44100
ts = 1/fs

fsinc = 1200
tsinc = 0.02

fpor = 1500
tpor = 0.00208 

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
for j in range(0,alto,2) :
	frec.append((fsinc, tsinc))
	frec.append((fpor, tpor))
	for i in range(ancho) : 
		frec.append((conv_frec(filas[j][i][0]), duracion))
	for i in range(ancho) :
		frec.append((conv_frec(filas[j][i][2]), duracion))
	for i in range(ancho) :
		frec.append((conv_frec(filas[j][i][1]), duracion))
	for i in range(ancho) : 
		frec.append((conv_frec(filas[j+1][i][0]), duracion))
datos = []
muestras = 0
offset = 0
for i, s in frec :
	muestras += s * fs
	x = int(muestras)
	
		
		
	for k in range(x) :
		datos.append(math.sin((2*math.pi*k*i*ts)+offset))
	offset += 2*math.pi*ts*(k+1)*i
	
	
	
	muestras -= x
	#print(muestras)

#time = range(0, len(datos))
#fig = plt.figure()
#ax = plt.subplot(211)
#ax.plot(time,datos)

#pylab.show()

audio = wave.open("audio.wav","wb")
num_canales = 1
bytes = 1
total_muestras = len(datos)
comptype = "NONE"
compname = "not compressed"

audio.setparams((num_canales,bytes,fs,total_muestras,comptype,compname))
#print(datos)
enteros = []
for v in datos:
    enteros.append(int((v*128)+128))

valores = []	
for y in enteros :
	if y == 256 :
		y = 255
		valores.append(y)
	else :
		valores.append(y)
#print(datos)
audio.writeframes(bytearray(valores))

audio.close()


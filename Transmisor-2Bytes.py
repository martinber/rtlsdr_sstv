from PIL import Image
import wave, math, struct
import matplotlib.pyplot as plt
import pylab
from resizeimage import resizeimage

imagen = Image.open("./informe/fotos_varias/double_cross_patio.jpg") #importa la imagen
im_re = imagen.resize((640,496), Image.BICUBIC) #reacomoda la imagen para que quede del tamaño deseado
imagen2 = im_re.convert('YCbCr') #Transformacion al formato deseado para la transmision

ancho = imagen2.width
alto  = imagen2.height

frec_negro = 1500
frec_blanco = 2300
rango = frec_blanco - frec_negro

tiempo = 120 #segundos
cant_valores = alto * ancho * 3 #cantidad de valores contando la intesidad, intensidad menos azul e intensidad menos rojo
duracion = 190*(10**-6) #la duración de cada uno de los valores del pixel en microsegundos

max_valor = 255 #determinado por (2^16)-1 por los bits

filas = []

fs = 48000
ts = 1/fs

fsinc = 1200 #frecuencia y tiempo de sincronización, que se envía al principio de cada línea de píxeles
tsinc = 0.02

fpor = 1500 # frecuencia y tiempo, que se envía luego de la de sincronización
tpor = 0.00208

for i in range(alto) :

	fila = []
	for j in range(ancho) :
		#print(i,j)
		fila.append(imagen2.getpixel((j,i))) #se obtienen los píxeles de la imagen


	filas.append(fila)

def conv_frec (valor_pixel) :
	valor = int(frec_negro + valor_pixel * rango/max_valor) #calcula la frecuencia que tiene cada valor de cada pixel

	return valor

frec = []
#val = 0
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

audio = wave.open("audio.wav","wb")
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

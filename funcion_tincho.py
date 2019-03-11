from PIL import Image as im
img = im.new('YCbCr',(4,4),"white")
datapixel = []
prev = []
def escribir_pixel(columna, linea, canal, valor):

    if canal == "lum":
        prev = datapixel[columna, linea]
        datapixel[columna, linea] = (valor, prev[1], prev[2])
    if canal == "cr":
        prev = datapixel[columna, linea]
        datapixel[columna, linea] = (prev[0], valor, prev[2])
    if canal == "cb":
        prev = datapixel[columna, linea]
        datapixel[columna, linea] = (prev[0], prev[1], valor)
    if canal == "next_lum":
        prev = datapixel[columna, linea]
        datapixel[columna, linea] = (valor, prev[1], prev[2])
    datapixel = img.load()
img.show(command='eom')

escribir_pixel(0, 0, "lum", 0)
escribir_pixel(0, 0, "cr", 128)
escribir_pixel(0, 0, "cb", 128)

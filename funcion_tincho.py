

def escribir_pixel(img, columna, linea, canal, valor):

    if canal == "lum":
        prev = img.getpixel((columna,linea-1))
        datapixel = (int((valor-1500)/800*255), prev[1], prev[2])
        #print(datapixel, valor)
        img.putpixel((columna,linea-1), datapixel)
    if canal == "cr":
        prev = img.getpixel((columna,linea-1))
        nxt_prev = img.getpixel((columna,linea))
        datapixel = (prev[0], prev[1], int((valor-1500)/800*255))
        nxt_datapixel = (nxt_prev[0], nxt_prev[1], int((valor-1500)/800*255))
        img.putpixel((columna,linea-1), datapixel)
        img.putpixel((columna,linea), nxt_datapixel)
    if canal == "cb":
        prev = img.getpixel((columna,linea-1))
        nxt_prev = img.getpixel((columna,linea))
        datapixel = (prev[0], int((valor-1500)/800*255), prev[2])
        nxt_datapixel = (nxt_prev[0], int((valor-1500)/800*255), nxt_prev[2])
        img.putpixel((columna,linea-1), datapixel)
        img.putpixel((columna,linea), nxt_datapixel)
    if canal == "nxt_lum":
        prev = img.getpixel((columna,linea))
        datapixel = (int((valor-1500)/800*255), prev[1], prev[2])
        img.putpixel((columna,linea), datapixel)

if __name__ == "__main__":
    from PIL import Image as im
    imagen = im.new('YCbCr',(300,300),"white")

    for i in range (0,101):
        escribir_pixel(imagen,i,i+1,"lum",2100)
        escribir_pixel(imagen,i,i+1,"cr",2300)
        escribir_pixel(imagen,i,i+1,"cb",1500)
        escribir_pixel(imagen,i,i+1,"nxt_lum",1800)
    imgconv = imagen.convert("RGB")
    imgconv.save("./test.png","PNG")

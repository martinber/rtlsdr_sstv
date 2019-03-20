import numpy
import math

def lowpass(cutout, delta_w, atten):
    '''
    Diseña un filtro pasa bajos, devuelve un vector con los coeficientes del
    filtro

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

    coeffs = numpy.kaiser(length, beta)

    # i es el indice en el vector, n es el eje con el cero centrado en el medio
    # del filtro
    # se suma 1 en el final del rango para que se incluya
    for i, n in enumerate(inc_range(
            int(-(length - 1) / 2),
            int((length - 1) / 2 + 1))):

        if n == 0:
            coeffs[i] *= cutout
        else:
            coeffs[i] *= math.sin(n * math.pi * cutout) / (n * math.pi)

    return coeffs

def filtrar(signal, coeffs):
    '''
    Filtra una señal (en un vector) usando los coeficientes (en otro vector)
    '''
    pass

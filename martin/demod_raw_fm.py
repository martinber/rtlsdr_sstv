import numpy #use numpy for buffers

import struct
import collections
import math
import sys

input_file = sys.argv[1]
output_file = sys.argv[2]

INPUT_RATE = 300e3
OUTPUT_RATE = 10e3

if INPUT_RATE % OUTPUT_RATE != 0:
    raise RuntimeError("Tasas de muestreo deben ser multiplos")

DECIMATION_FACTOR = int(INPUT_RATE / OUTPUT_RATE)

def write_complex_sample(filehandle, sample):
    '''
    escribir numero complejo (f32) en un archivo

    ejemplo:
        with open('data.raw', 'wb') as output_file:
            write_complex_sample(output_file, 3.2 + 1.2j)
    '''
    filehandle.write(struct.pack('<f', sample.real))
    filehandle.write(struct.pack('<f', sample.imag))

def write_sample(filehandle, sample):
    '''
    escribir numero real (f32) en un archivo

    ejemplo:
        with open('data.raw', 'wb') as output_file:
            write_sample(output_file, 3.2)
    '''
    filehandle.write(struct.pack('<f', sample))

def plot(vector1, vector2=None):
    import matplotlib.pyplot as plt
    import pylab

    fig = plt.figure()

    if vector2 is none:
        ax0 = plt.subplot(111)
        ax0.plot(range(len(vector1)), vector1)

    else:
        ax0 = plt.subplot(211)
        ax0.plot(range(len(vector1)), vector1)
        ax1 = plt.subplot(212)
        ax1.plot(range(len(vector2)), vector2)

    pylab.show()

def inc_range(a, b):
    '''range que incluye al valor final'''
    return range(a, b+1)

def lowpass(cutout, delta_w, atten):
    '''
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
    for i, n in enumerate(inc_range(
            int(-(length - 1) / 2),
            int((length - 1) / 2))):

        if n == 0:
            coeffs[i] *= cutout
        else:
            coeffs[i] *= math.sin(n * math.pi * cutout) / (n * math.pi)

    return coeffs

def decimate(input_gen, factor):
    '''
    La derecha del buff tiene la muestra mas reciente y tiene el indice mas alto
    El factor dice cuanto se va a decimar
    '''

    coeffs = lowpass(1./factor, 1./factor/2, 30)

    #  plot(coeffs, numpy.abs(numpy.fft.fft(coeffs)))

    buf = collections.deque([0] * len(coeffs))

    count = factor

    for s in input_gen:
        buf.popleft()
        buf.append(s)

        count -= 1

        if count == 0:
            count = factor
            sum = 0
            for j in range(len(coeffs)):
                sum += buf[-j - 1] * coeffs[j]

            yield sum

def demodulate_from_file(input_file):

    with open(input_file, 'rb') as input_file:

        prev_i = 0.0
        prev_q = 0.0

        while True:
            data = input_file.read(4*2)
            if not data:
                break
            i, q = struct.unpack('<2f', data)

            di = i - prev_i
            dq = q - prev_q

            try:
                freq = (i * dq - q * di) / (i**2 + q**2)
            except ZeroDivisionError:
                freq = 0

            yield freq

            prev_i = i
            prev_q = q

with open(output_file, 'wb') as output_file:
    for s in decimate(demodulate_from_file(input_file), DECIMATION_FACTOR):
        write_sample(output_file, s)

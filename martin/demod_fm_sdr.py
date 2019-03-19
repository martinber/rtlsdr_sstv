import SoapySDR
from SoapySDR import * #SOAPY_SDR_ constants
import numpy #use numpy for buffers

import struct
import collections
import math

# Parámetros del SDR, en Hz
RF_SAMPLE_RATE = 300000
RF_CARRIER_FREQ = 101.3e6
RF_BANDWIDTH = 180e3

# Parámetros usados para la decimación, en fracciones de pi radianes por segundo
# o en decibeles positivos
RF_FILTER_CUTOUT = 180e3 / (RF_SAMPLE_RATE / 2)
RF_FILTER_ATTEN = 30
RF_FILTER_DELTA_W = RF_FILTER_CUTOUT / 10

class Sdr:

    def __init__(self, sample_rate, carrier_freq, bandwidth):
        self.sample_rate = sample_rate
        self.carrier_freq = carrier_freq
        self.bandwidth = bandwidth

    def _generator(self):
        #receive some samples
        while True:
            sr = self.sdr.readStream(self.rxStream, [self.buff], len(self.buff))
            #  print(sr.ret) #num samples or error code
            #  print(sr.flags) #flags set by receive operation
            print(sr.timeNs) #timestamp for receive buffer
            for s in self.buff:
                yield s

    def __enter__(self):
        #enumerate devices
        results = SoapySDR.Device.enumerate()
        for result in results: print(result)

        #create device instance
        #args can be user defined or from the enumeration result
        args = dict(driver="rtlsdr")
        self.sdr = SoapySDR.Device(args)

        #query device info
        print(self.sdr.listAntennas(SOAPY_SDR_RX, 0))
        print(self.sdr.listGains(SOAPY_SDR_RX, 0))
        freqs = self.sdr.getFrequencyRange(SOAPY_SDR_RX, 0)
        for freqRange in freqs: print(freqRange)

        #apply settings
        self.sdr.setSampleRate(SOAPY_SDR_RX, 0, self.sample_rate)
        self.sdr.setFrequency(SOAPY_SDR_RX, 0, self.carrier_freq)
        self.sdr.setBandwidth(SOAPY_SDR_RX, 0, self.bandwidth)

        #setup a stream (complex floats)
        self.rxStream = self.sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)
        self.sdr.activateStream(self.rxStream) #start streaming

        #create a re-usable buffer for rx samples
        self.buff = numpy.array([0]*1024, numpy.complex64)

        return self._generator

    def __exit__(self, type, value, traceback):
        #shutdown the stream
        self.sdr.deactivateStream(self.rxStream) #stop streaming
        self.sdr.closeStream(self.rxStream)

def write_complex_sample(filehandle, sample):
    '''
    Escribir numero complejo (f32) en un archivo

    Ejemplo:
        with open('data.raw', 'wb') as output_file:
            write_complex_sample(output_file, 3.2 + 1.2j)
    '''
    filehandle.write(struct.pack('<f', sample.real))
    filehandle.write(struct.pack('<f', sample.imag))

def write_sample(filehandle, sample):
    '''
    Escribir numero real (f32) en un archivo

    Ejemplo:
        with open('data.raw', 'wb') as output_file:
            write_sample(output_file, 3.2)
    '''
    filehandle.write(struct.pack('<f', sample))

def inc_range(a, b):
    '''range que incluye al valor final'''
    return range(a, b+1)

def plot(vector1, vector2=None):
    import matplotlib.pyplot as plt
    import pylab

    fig = plt.figure()

    if vector2 is None:
        ax0 = plt.subplot(111)
        ax0.plot(range(len(vector1)), vector1)

    else:
        ax0 = plt.subplot(211)
        ax0.plot(range(len(vector1)), vector1)
        ax1 = plt.subplot(212)
        ax1.plot(range(len(vector2)), vector2)

    pylab.show()

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

def decimate(input_gen):
    '''
    La derecha del buff tiene la muestra mas reciente y tiene el indice mas alto
    '''

    coeffs = lowpass(RF_FILTER_CUTOUT, RF_FILTER_DELTA_W, RF_FILTER_ATTEN)

    #  plot(coeffs, numpy.abs(numpy.fft.fft(coeffs)))

    buf = collections.deque([0] * len(coeffs))

    for s in input_gen:
        buf.popleft()
        buf.append(s)
        sum = 0
        for j in range(len(coeffs)):
            sum += buf[-j - 1] * coeffs[j]

        yield sum

with Sdr(RF_SAMPLE_RATE, RF_CARRIER_FREQ, RF_BANDWIDTH) as sdr_gen, \
        open('gqrx_20190319_011314_101324000_{}_fc.raw'.format(int(RF_SAMPLE_RATE)), 'wb') as output_file:

    prev = 0.0 + 0.0j
    #  for s in decimate(sdr_gen()):
    for s in sdr_gen():

        i = s.real
        q = s.imag
        di = s.real - prev.real
        dq = s.imag - prev.imag

        #  print(i**2 + q**2)
        #  print(s)
        #  freq = (i * dq - q * di) / (i**2 + q**2)

        write_complex_sample(output_file, s)
        #  write_sample(output_file, freq)

        prev = s

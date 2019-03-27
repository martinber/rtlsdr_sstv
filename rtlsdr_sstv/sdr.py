import SoapySDR
from SoapySDR import * # SOAPY_SDR_ constants
import numpy as np
import math
import time, signal
import struct

class Sdr:

    def __init__(self, sample_rate, carrier_freq, bandwidth):
        self.sample_rate = sample_rate
        self.carrier_freq = carrier_freq
        self.bandwidth = bandwidth

    def _generator(self):
        #receive some samples
        while True:

            # len(self.buff) = numero de muestras que pido (1024)
            # sr.ret = numero de muestras recibidas

            sr = self.sdr.readStream(self.rxStream, [self.buff], len(self.buff))
            if sr.ret != len(self.buff):
                print(sr.ret) # numero de muestras recibidas

            if sr.ret > 0:
                for i in range(sr.ret):
                    yield self.buff[i]

    def __enter__(self):
        #enumerate devices
        #  results = SoapySDR.Device.enumerate()
        #  for result in results: print(result)

        #create device instance
        #args can be user defined or from the enumeration result
        args = dict(driver="rtlsdr")
        self.sdr = SoapySDR.Device(args)

        #query device info
        #  print(self.sdr.listAntennas(SOAPY_SDR_RX, 0))
        #  print(self.sdr.listGains(SOAPY_SDR_RX, 0))
        freqs = self.sdr.getFrequencyRange(SOAPY_SDR_RX, 0)
        #  for freqRange in freqs: print(freqRange)

        #apply settings
        self.sdr.setSampleRate(SOAPY_SDR_RX, 0, self.sample_rate)
        self.sdr.setFrequency(SOAPY_SDR_RX, 0, self.carrier_freq)
        self.sdr.setBandwidth(SOAPY_SDR_RX, 0, self.bandwidth)

        #setup a stream (complex floats)
        self.rxStream = self.sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)
        self.sdr.activateStream(self.rxStream) #start streaming

        #create a re-usable buffer for rx samples
        self.buff = np.array([0]*1024, np.complex64)

        return self._generator

    def __exit__(self, type, value, traceback):
        #shutdown the stream
        self.sdr.deactivateStream(self.rxStream) #stop streaming
        self.sdr.closeStream(self.rxStream)


def read_raw_samples(input_file, buf, num):
    '''
    Leer como maximo num muestras de un archivo, guardarlas en un
    buffer buf, y devolver la cantidad de muestras leidas
    '''
    for n in range(num):
        bytes = input_file.read(2*4) # 2 floats de 4 bytes
        if len(bytes) == 2*4:
            i, q = struct.unpack('<2f', bytes)
            buf[n] = i + 1j * q
        else:
            return n
    return n + 1

def siggen_app(
        filename,
        args,
        rate,
        ampl=0.7,
        freq=None,
        tx_bw=None,
        tx_chan=0,
        tx_gain=None,
        tx_ant=None,
        clock_rate=None,
        wave_freq=None
):
    """Generate signal until an interrupt signal is received."""

    if wave_freq is None:
        wave_freq = rate / 10

    sdr = SoapySDR.Device(args)
    #set clock rate first
    if clock_rate is not None:
        sdr.setMasterclock_rate(clock_rate)

    #set sample rate
    sdr.setSampleRate(SOAPY_SDR_TX, tx_chan, rate)
    print("Actual Tx Rate %f Msps"%(sdr.getSampleRate(SOAPY_SDR_TX, tx_chan) / 1e6))

    #set bandwidth
    if tx_bw is not None:
        sdr.setBandwidth(SOAPY_SDR_TX, tx_chan, tx_bw)

    #set antenna
    print("Set the antenna")
    if tx_ant is not None:
        sdr.setAntenna(SOAPY_SDR_TX, tx_chan, tx_ant)

    #set overall gain
    print("Set the gain")
    if tx_gain is not None:
        sdr.setGain(SOAPY_SDR_TX, tx_chan, tx_gain)

    #tune frontends
    print("Tune the frontend")
    if freq is not None:
        sdr.setFrequency(SOAPY_SDR_TX, tx_chan, freq)


    print("Create Tx stream")
    tx_stream = sdr.setupStream(SOAPY_SDR_TX, SOAPY_SDR_CF32, [tx_chan])
    print("Activate Tx Stream")
    sdr.activateStream(tx_stream)

    stream_mtu = sdr.getStreamMTU(tx_stream)
    buf = np.array([0]*stream_mtu, np.complex64)

    time_last_print = time.time()
    total_samps = 0

    state = dict(running=True)

    def signal_handler(signum, _):
        print('Signal handler called with signal {}'.format(signum))
        state['running'] = False

    signal.signal(signal.SIGINT, signal_handler)

    with open(filename, 'rb') as input_file:

        while state['running']:

            num = read_raw_samples(input_file, buf, stream_mtu)

            status = sdr.writeStream(tx_stream, [buf], num, timeoutUs=1000000)
            if status.ret != num:
                raise Exception("Expected writeStream() to consume all samples! %d" % status.ret)
            total_samps += status.ret

            if time.time() > time_last_print + 5.0:
                rate = total_samps / (time.time() - time_last_print) / 1e6
                print("Python siggen rate: %f Msps" % rate)
                total_samps = 0
                time_last_print = time.time()

            if num < stream_mtu:
                print("Terminado")
                break

    # escribir stream para obtener un timeout
    #  status = sdr.writeStream(tx_stream, [buf], num, timeoutUs=120_000_000)
    #  print(status)
    time.sleep(120)

    #cleanup streams
    print("Cleanup stream")
    sdr.deactivateStream(tx_stream)

    sdr.closeStream(tx_stream)
    print("Done!")

import SoapySDR
from SoapySDR import * # SOAPY_SDR_ constants
import numpy

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

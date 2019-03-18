import SoapySDR
from SoapySDR import * #SOAPY_SDR_ constants
import numpy #use numpy for buffers

class Sdr:

    def __init__(self, sample_rate, carrier_freq):
        self.sample_rate = sample_rate
        self.carrier_freq = carrier_freq

    def _generator(self):
        #receive some samples
        for i in range(10):
            sr = sdr.readStream(rxStream, [buff], len(buff))
            print(sr.ret) #num samples or error code
            print(sr.flags) #flags set by receive operation
            print(sr.timeNs) #timestamp for receive buffer
            for s in sr:
                yield s

    def __enter__(self):
        #enumerate devices
        results = SoapySDR.Device.enumerate()
        for result in results: print(result)

        #create device instance
        #args can be user defined or from the enumeration result
        args = dict(driver="rtlsdr")
        sdr = SoapySDR.Device(args)

        #query device info
        print(sdr.listAntennas(SOAPY_SDR_RX, 0))
        print(sdr.listGains(SOAPY_SDR_RX, 0))
        freqs = sdr.getFrequencyRange(SOAPY_SDR_RX, 0)
        for freqRange in freqs: print(freqRange)

        #apply settings
        sdr.setSampleRate(SOAPY_SDR_RX, 0, self.sample_rate)
        sdr.setFrequency(SOAPY_SDR_RX, 0, self.carrier_freq)

        #setup a stream (complex floats)
        rxStream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)
        sdr.activateStream(rxStream) #start streaming

        #create a re-usable buffer for rx samples
        buff = numpy.array([0]*1024, numpy.complex64)

        return _generator

    def __exit__(self, type, value, traceback):
        #shutdown the stream
        sdr.deactivateStream(rxStream) #stop streaming
        sdr.closeStream(rxStream)

with Sdr(sample_rate=1e6, carrier_freq=145.8e6) as samples:
    for sample in samples:
        print(sample)

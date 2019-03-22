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
            #  print(sr.timeNs) #timestamp for receive buffer
            for s in self.buff:
                yield s

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
        self.buff = numpy.array([0]*1024, numpy.complex64)

        return self._generator

    def __exit__(self, type, value, traceback):
        #shutdown the stream
        self.sdr.deactivateStream(self.rxStream) #stop streaming
        self.sdr.closeStream(self.rxStream)


def siggen_app(
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
    phase_acc = 0
    phase_inc = 2*math.pi*wave_freq/rate
    stream_mtu = sdr.getStreamMTU(tx_stream)
    samps_chan = np.array([ampl]*stream_mtu, np.complex64)

    time_last_print = time.time()
    total_samps = 0

    state = dict(running=True)

    def signal_handler(signum, _):
        print('Signal handler called with signal {}'.format(signum))
        state['running'] = False

    signal.signal(signal.SIGINT, signal_handler)

    while state['running']:
        phase_acc_next = phase_acc + stream_mtu*phase_inc
        phases = np.linspace(phase_acc, phase_acc_next, stream_mtu)
        samps_chan = ampl*np.exp(1j * phases).astype(np.complex64)
        phase_acc = phase_acc_next
        while phase_acc > math.pi * 2:
            phase_acc -= math.pi * 2

        status = sdr.writeStream(tx_stream, [samps_chan], samps_chan.size, timeoutUs=1000000)
        if status.ret != samps_chan.size:
            raise Exception("Expected writeStream() to consume all samples! %d" % status.ret)
        total_samps += status.ret

        if time.time() > time_last_print + 5.0:
            rate = total_samps / (time.time() - time_last_print) / 1e6
            print("Python siggen rate: %f Msps" % rate)
            total_samps = 0
            time_last_print = time.time()

    #cleanup streams
    print("Cleanup stream")
    sdr.deactivateStream(tx_stream)
    sdr.closeStream(tx_stream)
    print("Done!")

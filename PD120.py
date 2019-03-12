from __future__ import division, with_statement
from six.moves import range
from six.moves import map
from six.moves import zip
from math import sin, pi
from random import random
from contextlib import closing
from itertools import cycle, chain
from array import array
import wave

FREQ_VIS_BIT1 = 1100
FREQ_SYNC = 1200
FREQ_VIS_BIT0 = 1300
FREQ_BLACK = 1500
FREQ_VIS_START = 1900
FREQ_WHITE = 2300
FREQ_RANGE = FREQ_WHITE - FREQ_BLACK
FREQ_FSKID_BIT1 = 1900
FREQ_FSKID_BIT0 = 2100

MSEC_VIS_START = 300
MSEC_VIS_SYNC = 10
MSEC_VIS_BIT = 30
MSEC_FSKID_BIT = 22


class SSTV(object):

    def __init__(self, image, samples_per_sec, bits):
        self.image = image
        self.samples_per_sec = samples_per_sec
        self.bits = bits
        self.vox_enabled = False
        self.fskid_payload = ''
        self.nchannels = 1
        self.on_init()

    def on_init(self):
        pass

    BITS_TO_STRUCT = {8: 'b', 16: 'h'}

    def write_wav(self, filename):
        """writes the whole image to a Microsoft WAV file"""
        fmt = self.BITS_TO_STRUCT[self.bits]
        data = array(fmt, self.gen_samples())
        if self.nchannels != 1:
            data = array(fmt, chain.from_iterable(
                zip(*([data] * self.nchannels))))
        with closing(wave.open(filename, 'wb')) as wav:
            wav.setnchannels(self.nchannels)
            wav.setsampwidth(self.bits // 8)
            wav.setframerate(self.samples_per_sec)
            wav.writeframes(data.tostring())

    def gen_samples(self):
        """generates discrete samples from gen_values()
           performs quantization according to
           the bits per sample value given during construction
        """
        max_value = 2 ** self.bits
        alias = 1 / max_value
        amp = max_value // 2
        lowest = -amp
        highest = amp - 1
        alias_cycle = cycle((alias * (random() - 0.5) for _ in range(1024)))
        for value, alias_item in zip(self.gen_values(), alias_cycle):
            sample = int(value * amp + alias_item)
            yield (lowest if sample <= lowest else
                sample if sample <= highest else highest)

    def gen_values(self):
        """generates samples between -1 and +1 from gen_freq_bits()
           performs sampling according to
           the samples per second value given during construction
        """
        spms = self.samples_per_sec / 1000
        offset = 0
        samples = 0
        factor = 2 * pi / self.samples_per_sec
        sample = 0
        for freq, msec in self.gen_freq_bits():
            samples += spms * msec
            tx = int(samples)
            freq_factor = freq * factor
            for sample in range(tx):
                yield sin(sample * freq_factor + offset)
            offset += (sample + 1) * freq_factor
            samples -= tx

    def gen_freq_bits(self):
        """generates tuples (freq, msec) that describe a sine wave segment
           frequency "freq" in Hz and duration "msec" in ms
        """
        if self.vox_enabled:
            for freq in (1900, 1500, 1900, 1500, 2300, 1500, 2300, 1500):
                yield freq, 100
        yield FREQ_VIS_START, MSEC_VIS_START
        yield FREQ_SYNC, MSEC_VIS_SYNC
        yield FREQ_VIS_START, MSEC_VIS_START
        yield FREQ_SYNC, MSEC_VIS_BIT  # start bit
        vis = self.VIS_CODE
        num_ones = 0
        for _ in range(7):
            bit = vis & 1
            vis >>= 1
            num_ones += bit
            bit_freq = FREQ_VIS_BIT1 if bit == 1 else FREQ_VIS_BIT0
            yield bit_freq, MSEC_VIS_BIT
        parity_freq = FREQ_VIS_BIT1 if num_ones % 2 == 1 else FREQ_VIS_BIT0
        yield parity_freq, MSEC_VIS_BIT
        yield FREQ_SYNC, MSEC_VIS_BIT  # stop bit
        for freq_tuple in self.gen_image_tuples():
            yield freq_tuple
        for fskid_byte in map(ord, self.fskid_payload):
            for _ in range(6):
                bit = fskid_byte & 1
                fskid_byte >>= 1
                bit_freq = FREQ_FSKID_BIT1 if bit == 1 else FREQ_FSKID_BIT0
                yield bit_freq, MSEC_FSKID_BIT

    def gen_image_tuples(self):
        return []

    def add_fskid_text(self, text):
        self.fskid_payload += '\x20\x2a{0}\x01'.format(
                ''.join(chr(ord(c) - 0x20) for c in text))

    def horizontal_sync(self):
        yield FREQ_SYNC, self.SYNC


def byte_to_freq(value):
    return FREQ_BLACK + FREQ_RANGE * value / 255

-----------------------------------------------------------------------------

from __future__ import division
from six.moves import range
from pysstv.sstv import SSTV, byte_to_freq


class GrayscaleSSTV(SSTV):
    def on_init(self):
        self.pixels = self.image.convert('LA').load()

    def gen_image_tuples(self):
        for line in range(self.HEIGHT):
            for item in self.horizontal_sync():
                yield item
            for item in self.encode_line(line):
                yield item

    def encode_line(self, line):
        msec_pixel = self.SCAN / self.WIDTH
        image = self.pixels
        for col in range(self.WIDTH):
            pixel = image[col, line]
            freq_pixel = byte_to_freq(pixel[0])
	yield freq_pixel, msec_pixel

----------------------------------------------------------------------------------------

from __future__ import division
from six.moves import range, zip
from pysstv.sstv import byte_to_freq, FREQ_BLACK, FREQ_WHITE, FREQ_VIS_START
from pysstv.grayscale import GrayscaleSSTV
from itertools import chain


RED, GREEN, BLUE = range(3)


class ColorSSTV(GrayscaleSSTV):
    def on_init(self):
        self.pixels = self.image.load()

    def encode_line(self, line):
        msec_pixel = self.SCAN / self.WIDTH
        image = self.pixels
        for index in self.COLOR_SEQ:
            for item in self.before_channel(index):
                yield item
            for col in range(self.WIDTH):
                pixel = image[col, line]
                freq_pixel = byte_to_freq(pixel[index])
                yield freq_pixel, msec_pixel
            for item in self.after_channel(index):
                yield item

    def before_channel(self, index):
        return []

	after_channel = before_channel

------------------------------------------------------------
class PD90(ColorSSTV):
    VIS_CODE = 0x63
    WIDTH = 320
    HEIGHT = 256
    SYNC = 20
    PORCH = 2.08
    PIXEL = 0.532

    def gen_image_tuples(self):
        yuv = self.image.convert('YCbCr').load()
        for line in range(0, self.HEIGHT, 2):
            for item in self.horizontal_sync():
                yield item
            yield FREQ_BLACK, self.PORCH
            pixels0 = [yuv[col, line] for col in range(self.WIDTH)]
            pixels1 = [yuv[col, line + 1] for col in range(self.WIDTH)]
            for p in pixels0:
                yield byte_to_freq(p[0]), self.PIXEL
            for p0, p1 in zip(pixels0, pixels1):
                yield byte_to_freq((p0[2] + p1[2]) / 2), self.PIXEL
            for p0, p1 in zip(pixels0, pixels1):
                yield byte_to_freq((p0[1] + p1[1]) / 2), self.PIXEL
            for p in pixels1:
	yield byte_to_freq(p[0]), self.PIXEL

class PD120(PD90):
    VIS_CODE = 0x5f
    WIDTH = 640
    HEIGHT = 496
	PIXEL = 0.19
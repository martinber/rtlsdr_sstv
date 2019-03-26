from sdr import Sdr
import raw_file
import dsp
import demod_sstv

import signal
import struct

RF_BANDWIDTH = 180e3

def main(args):

    if not args.from_demod_raw:

        if not args.from_tmp_raw:

            print("Recibiendo muestras desde SDR...")

            print("Archivo temporal: {}", args.tmp_raw)
            print("Frecuencia: {}", args.rf_freq)
            print("Tasa de muestreo: {}", args.rf_rate)
            print("Presione Ctrl-C para parar la recepción..,")

            sdr_to_raw(args.tmp_raw, args.rf_freq, args.rf_rate)

        print("Demodulando FM...")

        sstv_signal = list(raw_demod(args.tmp_raw, args.fm_demod_gain))

        print("Diezmando...")

        sstv_signal = decimate(sstv_signal, args.rf_rate, args.audio_rate)

        print("Normalizando...")

        sstv_signal = normalize(sstv_signal)

        # Si se eligió la opción para exportar archivo RAW demodulado
        if args.demod_raw:
            with open(args.demod_raw, 'wb') as output_file:
                for s in sstv_signal:
                    raw_file.write_sample(output_file, s)

    else:
        sstv_signal = []

        with open(args.demod_raw, 'rb') as input_file:

            while True:
                data = input_file.read(4) # 4 bytes (float)
                if not data:
                    break

                # Devuelve un tuple de un unico elemento
                sample = struct.unpack('<f', data)[0]

                sstv_signal.append(sample)

    print("Demodulando SSTV...")

    demod_sstv.inicializar_demod(sstv_signal, args.image, args.audio_rate)



def sdr_to_raw(filename, rf_freq, rf_rate):
    '''
    Recibir muestras desde SDR y guardarlas en un RAW hasta que se presione
    Ctrl-C
    '''

    global INTERRUPT
    INTERRUPT = False

    def signal_handler(signal, frame):
        '''
        Se ejecuta al recibir una señal.

        Suscrito a SIGINT (Ctrl-C).
        '''
        global INTERRUPT
        INTERRUPT = True

    # Capturar SIGINT
    signal.signal(signal.SIGINT, signal_handler)

    with Sdr(rf_rate, rf_freq, RF_BANDWIDTH) as sdr_gen, \
            open(filename, 'wb') as output_file:

        for s in sdr_gen():
            raw_file.write_complex_sample(output_file, s)

            if INTERRUPT:
                break

    print("Recibido Ctrl-C, parando recepción")

    # Dejar de capturar SIGINT
    signal.signal(signal.SIGINT, signal.SIG_DFL)

def raw_demod(input_file, gain):
    '''
    Generador que devuelve muestras demoduladas tomadas desde un RAW

    Se debe dar una ganancia, no hay que saturar. Como son floats no hay
    problema de elegir una ganancia muy chica.
    '''

    with open(input_file, 'rb') as input_file:

        prev_i = 0.0
        prev_q = 0.0

        while True:
            data = input_file.read(4*2) # 4 bytes (float) * 2 (i, q)
            if not data:
                break
            i, q = struct.unpack('<2f', data)

            di = i - prev_i
            dq = q - prev_q

            try:
                freq = gain * (i * dq - q * di) / (i*i + q*q)
            except ZeroDivisionError:
                freq = 0

            yield freq

            prev_i = i
            prev_q = q

def decimate(samples, input_rate, output_rate):
    '''
    Decimar señal de entrada y filtrar.
    '''

    factor = input_rate / output_rate

    if factor % 1 != 0:
        print("Tasas de muestreo deben ser múltiplos")
        sys.exit(1)

    factor = int(factor)
    cutout = 2800 / (output_rate / 2)
    delta_w = cutout/5

    coeffs = dsp.lowpass(cutout, delta_w, 30)

    print("Largo de filtro: {}".format(len(coeffs)))
    print("Factor: {}".format(factor))

    output = []

    for i in range(len(samples)):

        # Si esta muestra sobrevive al diezmado
        if i % factor == 0:

            sum = 0
            for j in range(len(coeffs)):
                sum += samples[i - j] * coeffs[j]
            output.append(sum)

    return output

def normalize(sstv_signal):

    _sum = sum(sstv_signal)
    _max = max(sstv_signal)
    _min = min(sstv_signal)
    _len = len(sstv_signal)
    _range = (_max - _min) / 2

    average = _sum / _len

    return list(map(lambda s: (s - average) / _range, sstv_signal))

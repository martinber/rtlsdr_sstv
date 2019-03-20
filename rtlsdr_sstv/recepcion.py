from sdr import Sdr
import raw_file

def main(args):
    print(args)

    sdr_to_raw(args.tmp_raw, args.rf_freq, args.rf_rate)


def sdr_to_raw(filename, rf_freq, rf_rate):
    '''
    Recibir muestras desde SDR y guardarlas en un WAV hasta que se presione
    Ctrl-C
    '''

    RF_BANDWIDTH = 180e3

    with Sdr(rf_rate, rf_freq, RF_BANDWIDTH) as sdr_gen, \
            open(filename, 'wb') as output_file:

        for s in sdr_gen():
            raw_file.write_complex_sample(output_file, s)

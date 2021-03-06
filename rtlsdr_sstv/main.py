'''
Punto de entrada al programa.

Leer argumentos de entrada y llamar a recepcion.main(args) o transmision(args)

Argumentos leidos en RX y TX:

- `args.rf_freq`: float.
- `args.rf_rate`: float.
- `args.audio_rate`: float.
- `args.image`: str.

Argumentos leidos en RX:

- `args.tmp_raw`: str.
- `args.demod_raw`: str o None si no se guarda el RAW.
- `args.from_tmp_raw`: bool.
- `args.fm_demod_gain`: float.

Argumentos leidos en TX:

- `args.sstv_wav`: str o None si no se guarda el WAV.
- `args.soapy_args`: str.
- `args.rf_ant`: str.
- `args.rf_gain`: int.
- `args.mod_gain`: int.
- `args.tmp_raw`: str.
- `args.demod_raw`: str o None si no se guarda el RAW.
'''

import argparse
import recepcion
import transmision

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help='comandos', dest='comando')
subparsers.required = True

# Argumentos RX y TX

parser.add_argument(
        '-f', '--rf-freq', type=float,
        help=('Frecuencia de transmision o recepción de RF en Hz, por defecto: '
              '137.2e6 para trabajar en los 137.2MHz'),
        default=462.552e6,
)
parser.add_argument(
        '--rf-rate', type=float,
        help=('Tasa de muestreo a usar al trabajar en RF, escribir en Hz, por '
              'defecto: 300e3 para usar el SDR con en los 300ksps. Ver en GQRX '
              'las tasas posibles, creo que son 100ksps, 300ksps, 960ksps, y '
              'mas de eso no haría falta. Debe ser múltiplo de --audio-rate'),
        default=300e3,
)
parser.add_argument(
        '--audio-rate', type=float,
        help=('Tasa de muestreo a usar al trabajar en audio, escribir en Hz, '
              'por defecto: 10e3 para trabajar con audios a 10kHz. Usar tasas '
              'que sean fracciones enteras de --rf-rate'),
        default=10e3,
)

# Argumentos RX

parser_rx = subparsers.add_parser('rx', help='recibir SSTV')
parser_rx.add_argument(
        'image', type=str,
        help=('Nombre de imagen a recibir, debe ser un PNG'),
        default='./recepcion.png',
)
parser_rx.add_argument(
        '--tmp-raw', type=str,
        help=('Nombre de archivo RAW temporal en donde guardar muestras '
              'recibidas'),
        default='./tmp_rx.raw',
)
parser_rx.add_argument(
        '--demod-raw', type=str,
        help=('Nombre de archivo RAW donde guardar muestras demoduladas. '
              'Opcional'),
        default=None,
)
parser_rx.add_argument(
        '--from-tmp-raw', action='store_true',
        help=('Demodular desde muestras en RAW en lugar de recibir desde SDR'),
)
parser_rx.add_argument(
        '--from-demod-raw', action='store_true',
        help=('Demodular SSTV a partir de FM previamente demodulado, se debe '
              'especificar --demod-raw'),
)
parser_rx.add_argument(
        '--fm-demod-gain', type=float,
        help=('Ganancia del demodulador FM. Por defecto: 0.2'),
        default=0.2,
)

# Argumentos TX

parser_tx = subparsers.add_parser('tx', help='transmitir SSTV')
parser_tx.add_argument(
        'image', type=str,
        help=('Nombre de imagen a transmitir, debe ser un PNG'),
)
parser_tx.add_argument(
        '--sstv-wav', type=str,
        help=('Nombre archivo WAV en donde guardar el SSTV generado, opcional'),
        default=None,
)
parser_tx.add_argument(
        '--soapy-args', type=str,
        help=('Argumentos para SoapySDR, por defecto: "driver=lime"'),
        default='driver=lime',
)
parser_tx.add_argument(
        '--rf-ant', type=str,
        help=('Antena a utilizar, ver las posibles usando '
              '`SoapySDRUtil --probe`, por defecto: "Auto"'),
        default='Auto',
)
parser_tx.add_argument(
        '--rf-gain', type=int,
        help=('Ganancia de transmisión utilizada en dB, por defecto: 20'),
        default=20,
)
parser_tx.add_argument(
        '--mod-gain', type=float,
        help=('Ganancia de modulación, influye en el índice de modulación de '
              'FM, por defecto: 10'),
        default=10,
)
parser_tx.add_argument(
        '--tmp-raw', type=str,
        help=('Nombre de archivo RAW temporal en donde guardar muestras '
              'a transmitir'),
        default='./tmp_tx.raw',
)
parser_tx.add_argument(
        '--from-tmp-raw', action='store_true',
        help=('Transmitir muestras previamente moduladas en un archivo RAW '
              'temporal'),
)

args = parser.parse_args()

if args.comando == 'rx':
    recepcion.main(args)
elif args.comando == 'tx':
    transmision.main(args)
else:
    RuntimeError('Comando desconocido')

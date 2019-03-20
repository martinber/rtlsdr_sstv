import argparse
import recepcion
import transmision

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help='comandos', dest='comando')
subparsers.required = True

parser.add_argument('-f', '--freq', type=int,
        help="frecuencia de muestreo")

parser_rx = subparsers.add_parser('rx', help='recibir SSTV')

parser_tx = subparsers.add_parser('tx', help='transmitir SSTV')

args = parser.parse_args()



if args.comando == 'rx':

    recepcion.main(args)


elif args.comando == 'tx':

    transmision.main(args)

else:
    RuntimeError('Comando desconocido')

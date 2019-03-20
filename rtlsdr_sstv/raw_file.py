import struct

def write_complex_sample(filehandle, sample):
    '''
    escribir numero complejo (f32) en un archivo

    ejemplo:
        with open('data.raw', 'wb') as output_file:
            write_complex_sample(output_file, 3.2 + 1.2j)
    '''
    filehandle.write(struct.pack('<f', sample.real))
    filehandle.write(struct.pack('<f', sample.imag))

def write_sample(filehandle, sample):
    '''
    escribir numero real (f32) en un archivo

    ejemplo:
        with open('data.raw', 'wb') as output_file:
            write_sample(output_file, 3.2)
    '''
    filehandle.write(struct.pack('<f', sample))

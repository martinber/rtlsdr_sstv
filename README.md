# SSTV

## Sobre LimeSDR

https://wiki.myriadrf.org/LimeSDR-USB

ISS usa el modo PD120

Resolucion 640x496.

## Librerías

- https://github.com/roger-/pyrtlsdr.

- Para imagenes: https://python-pillow.org/.

- Para cosas de matematica: Numpy (pero no me gusta mucho, no haría falta
  usarla)..

- Para hacer graficos: Matplotlib.

- Para trabajar con archivos WAV: Buscar.

## Tutoriales

- https://witestlab.poly.edu/blog/capture-and-decode-fm-radio/#tldrversion

## Notas

- http://www.classicsstv.com/pdmodes.php

- Explicaciones sobre todos los modos: http://www.sstv-handbook.com/download/sstv_04.pdf

- Codigos que usa los modos: http://www.g0hwc.com/sstv_modes.html

- Sitio sobre SSTV con audio: https://www.nonstopsystems.com/radio/frank_radio_sstv.htm

- Info varia y links: https://inst.eecs.berkeley.edu/~ee123/fa12/project.html

- Sobre demodulacion avanzada: http://lionel.cordesses.free.fr/gpages/Cordesses.pdf

- RDS aparentemente transmite a 1-2kb/s. un PNG que tengo pesa 11KiB. RDS2 soporta
  imagenes de max. 4KB: JPG, PNG o GIF.

### Tiempo transmision

Segun: http://f1ult.free.fr/DIGIMODES/MULTIPSK/sstv_en.htm

PD 120 (RX only): color mode, transmission time: 126 s,

### Espectrograma de QSSTV

Spectrum and Waterfall:
There are three markers for SSTV (red lines):

- 1200: Sync frequency
- 1500: Lower video frequency
- 2300: Upper video frequency In DRM, the markers indicate the 3 unmodulated carrier frequencies

### Encajar SSTV en broadcast FM

- RDS: https://en.wikipedia.org/wiki/Radio_Data_System

- Alguien que capaz que ya lo haya hecho: https://github.com/zouppen/subcarrier-sstv

### Sobre SSBSC para stereo:

- https://www.radioworld.com/news-and-business/ssbsc-a-winwin-for-fm-radio

- https://www.nab.org/xert/scitech/pdfs/rd040912.pdf

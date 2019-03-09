# SSTV PD120

ISS usa el modo PD120

## Notas sobre modos SSTV

- http://www.classicsstv.com/pdmodes.php

- Explicaciones sobre todos los modos: http://www.sstv-handbook.com/download/sstv_04.pdf

- Codigos que usa los modos: http://www.g0hwc.com/sstv_modes.html

- Sitio sobre SSTV con audio: https://www.nonstopsystems.com/radio/frank_radio_sstv.htm

- Info varia y links: https://inst.eecs.berkeley.edu/~ee123/fa12/project.html

- Sobre demodulacion avanzada: http://lionel.cordesses.free.fr/gpages/Cordesses.pdf

- Resolución 640x496.

- Tiempo de transmisión 120s. Aunque segun
    [esta pagina](http://f1ult.free.fr/DIGIMODES/MULTIPSK/sstv_en.htm) son 126s.

## Espectrograma de QSSTV

Esto es lo que muestra el espectrograma de la derecha del programa QSSTV.

There are three markers for SSTV (red lines):

- 1200: Sync frequency

- 1500: Lower video frequency

- 2300: Upper video frequency In DRM, the markers indicate the 3 unmodulated carrier frequencies

## Programación

### Librerías

- Para imagenes: https://python-pillow.org/

- Para cosas de matematica: Numpy (pero no me gusta mucho, no haría falta
  usarla).

- Para hacer graficos: Matplotlib.

- Para trabajar con archivos WAV: Buscar.

- Para trabajar con LimeSDR y RTL-SDR: https://github.com/pothosware/SoapySDR/wiki/PythonSupport

- Para trabajar solamente con RTL-SDR: https://github.com/roger-/pyrtlsdr

### Tutoriales y ejemplos

- Demodulacion FM: https://witestlab.poly.edu/blog/capture-and-decode-fm-radio/#tldrversion

- Transmision de SSB usando SoapySDR: https://github.com/pothosware/SoapySDR/blob/master/python/apps/SimpleSiggen.py

### Sobre LimeSDR

- https://www.crowdsupply.com/lime-micro/limesdr-mini

- https://wiki.myriadrf.org/LimeSDR-Mini

### Link de transmisor SSTV

https://github.com/dnet/pySSTV

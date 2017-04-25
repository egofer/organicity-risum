 #!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

#  Constantes

HOME = os.path.expanduser('~/RISUM/GTFS/')
SOFTWARE = ['gnumeric', 'spatialite_osm_map', 'sqlite3']  # Software requerido
BBOX = "-3.95,43.378,-3.73,43.50"  # Envolvente de descarga de cartografía
RELACIONES = os.path.expanduser('~/RISUM/CSV/relaciones_rutas_transporte.csv')
TIEMPOS_PARADAS = os.path.expanduser('~/RISUM/CSV/tiempos_paradas.ods')
GTFS_ODS = os.path.expanduser('~/RISUM/CSV/santander.gtfs.ods')
GTFS_DIR = os.path.expanduser('/var/tmp/gtfs/')
OTP = os.path.expanduser(r"~/RISUM/OTP/") #Directorio de descarga de OpenTripPlanner
OPENSHIFT_DIR = "xxxxxxxxxxxxxxx@santandergo-altergeo.rhcloud.com:/var/lib/openshift/xxxxxxxxxxxxxxx/app-root/data/sdr/"

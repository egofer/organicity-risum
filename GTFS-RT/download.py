#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Captura los datos de posición de vehículos de Santander Open Data y los almacena
en una base de datos SQLite
"""

__author__ = "Emilio Gomez Fernandez"

__version__ = "0.3"
__maintainer__ = "Emilio Gomez Fernandez"
__email__ = "emiliogf@altergeosistemas.com"
__status__ = "Development"
__date__ = "March, 2017"

import os
import sqlite3
from colorama import Fore, init, Back
# Reinicializa colorama a sus estado original tras cada mensaje
init(autoreset=True)

VEHICLES_POSITIONS = 'http://datos.santander.es/api/rest/datasets/control_flotas_posiciones.csv?items=50000'
TRIP_UPDATES = 'http://datos.santander.es/api/rest/datasets/control_flotas_estimaciones.csv?items=50000'
STOP_TIMES = 'http://datos.santander.es/api/rest/datasets/programacionTUS_horariosLineas.csv?items=50000'
DAILY_CARDS = 'http://datos.santander.es/api/rest/datasets/programaTUS_horariosTarjetas.csv?items=50000'
WORK_CALENDAR = 'http://datos.santander.es/api/rest/datasets/calendario_laboral.csv?items=50000'
#DIR_TMP = os.environ["OPENSHIFT_TMP_DIR"]
#DIR_TMP = os.environ["OPENSHIFT_DATA_DIR"]
DIR_TMP = '/tmp/'


def create_tables():
    u"""Crea ls tablas en SQLite necesarias para realizar la importación."""
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          "Creando las tablas en la base de datos '" + DIR_TMP + "bustus.sqlite'")
    comando = '/usr/bin/sqlite3 ' + DIR_TMP + 'bustus.sqlite < "' + DIR_TMP + 'tables.sql"'
    os.system(comando)
    return


def import_files():
    u"""Descarga los archivos csv de posición de autobuses y estimación de parada y los importa a una base de datos SQLite."""
    archivos = {'control_flotas_posiciones': VEHICLES_POSITIONS, 'control_flotas_estimaciones': TRIP_UPDATES,
                'programacionTUS_horariosLineas': STOP_TIMES, 'programaTUS_horariosTarjetas': DAILY_CARDS, 'calendario_laboral': WORK_CALENDAR}
    for archivo, url in archivos.items():
        print(Fore.GREEN + "AVISO:" + Fore.RESET +
              "Descargando  archivo " + Fore.CYAN + archivo + Fore.RESET + " en " + DIR_TMP)
        os.system('wget -O ' + DIR_TMP + archivo + '.csv ' + url)
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          "Importando archivos CSV en la base de datos '" + DIR_TMP + "bustus.sqlite'")

    archi = open(DIR_TMP + 'import.txt', 'w')
    archi.write(".separator ','\n")
    archi.write(".import " + DIR_TMP + "control_flotas_posiciones.csv control_flotas_posiciones\n")
    archi.write(".import " + DIR_TMP + "control_flotas_estimaciones.csv control_flotas_estimaciones\n")
    archi.write(".import " + DIR_TMP + "programacionTUS_horariosLineas.csv programacionTUS_horariosLineas\n")
    archi.write(".import " + DIR_TMP + "programaTUS_horariosTarjetas.csv programaTUS_horariosTarjetas\n")
    archi.write(".import " + DIR_TMP + "calendario_laboral.csv calendario_laboral\n")
    archi.close()
    comando = '/usr/bin/sqlite3 ' + DIR_TMP + 'bustus.sqlite < "' + DIR_TMP + 'import.txt" > /dev/null 2>&1'
    os.system(comando)
    # Elimina la primera fila porque al importar introduce el nombre de la
    # columna.
    con = sqlite3.connect(DIR_TMP +'bustus.sqlite')
    cursor = con.cursor()
    for tabla in archivos:
        print(Fore.GREEN + "AVISO:" + Fore.RESET + "Eliminando para la tabla " + Fore.CYAN +
              tabla + Fore.RESET + " la primera fila que contiene el nombre de las columnas.")
        sql = "DELETE FROM " + tabla + " WHERE ROWID = 1"
        cursor.execute(sql)
    con.commit()
    cursor.close()
    return


def day_week():
    u"""Actualiza la tabla de posición de vehículos con el día de la semana de la fecha 'ayto:instante'"""
    print(Fore.GREEN + "AVISO:" + Fore.RESET + "Calculando el día de la semana para la tabla " +
          Fore.CYAN + "programacionTUS_horariosLineas" + Fore.RESET + ".")
    con = sqlite3.connect(DIR_TMP + 'bustus.sqlite')
    cursor = con.cursor()
    sql = 'ALTER TABLE programacionTUS_horariosLineas ADD COLUMN dia_semana INTEGER'
    cursor.execute(sql)
    sql = 'UPDATE programacionTUS_horariosLineas SET dia_semana = strftime("%w", "dc:modified");'
    cursor.execute(sql)
    sql = ('UPDATE programacionTUS_horariosLineas SET dia_semana = strftime("%w", "dc:modified") - 1'
           ' WHERE "ayto:hora" > 86400;')  # Si ayto:instante supera las 23:59:59 significa que la ruta pertene al día anterior.
    cursor.execute(sql)
    if cursor.rowcount > 0:
        print(Fore.GREEN + "AVISO:" + Fore.RESET +
              "Se ha calculado el día para horarios que sobrepasan las 23:59:59.")
    con.commit()
    cursor.close()
    return


def calc_trip_id():
    u"""Calcula el trip_id de los vehículos en función de la tabla horarios por parada"""
    print(Fore.GREEN + "AVISO:" + Fore.RESET + "Capturando el trip_id de cada viaje y creando la tabla " +
          Fore.CYAN + "posicion_vehiculos" + Fore.RESET + ".")
    # Seleccionar de la tabla "horarios_parada" el campo "dc:identifier" cuando
    # el campo "ayto:servicio" coincida con el campo "ayto:servicio" de la tabla
    # "posicion_vehiculos" y siempre que "ayto:instante" de esta tabla sea igual
    # o mayor que el campo "ayto:hora" de la tabla "horarios_parada" y coincida
    # el mismo día de la semana.
    con = sqlite3.connect(DIR_TMP + 'bustus.sqlite')
    cursor = con.cursor()
    # En SQLite no es posible utilizar JOINS en clausulas UPDATE porque lo que creo otra tabla
    # TODO: Existe un problema con las líneas buho que coge el trip_id del día
    # actual, cuando debería ser el anterior.

    # TODO: En la clausula WHERE ... TIME ...  los buho tendría que coger el día anterior.
    sql = """CREATE TABLE posicion_vehiculos AS
            SELECT a."dc:identifier" AS trip_id ,
            b."ayto:vehiculo" AS "ayto:vehiculo",
            b."ayto:indice" AS "ayto:indice",
            b."ayto:linea" AS "ayto:linea",
            b."ayto:coche" AS "ayto:coche",
            b."ayto:servicio" AS "ayto:servicio",
            b."wgs84_pos:lat" AS "wgs84_pos:lat",
            b."wgs84_pos:long" AS "wgs84_pos:long",
            b."ayto:velocidad" AS "ayto:velocidad",
            a."ayto:idevento" AS "ayto:idevento",
            b."ayto:instante" AS "ayto:instante",
            b."dc:modified" AS "dc:modified"
            FROM programaciontus_horarioslineas AS a
            LEFT JOIN control_flotas_posiciones AS b
            ON a."ayto:servicio" = b."ayto:servicio"
            WHERE strftime("%s","1970-01-01 " || TIME(b."ayto:instante")) >= a."ayto:hora"
            AND strftime("%w", b."ayto:instante") = a.dia_semana
            AND b."ayto:indice" = 0
            AND a."ayto:idEvento" IN (3,11)"""

    cursor.execute(sql)
    con.commit()
    cursor.close()
    con.close()
    return

if __name__ == "__main__":
    create_tables()
    import_files()
    day_week()
    calc_trip_id()

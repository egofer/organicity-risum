#!/usr/bin/env python
#-*- coding: utf-8 -*-

u"""Genera feeds GTFS estáticos a partir de datos de la empresa de autobuses TUS.
Ejemplo de ejecución:
python main.py -osm -shp -fv -sv

"""

__author__ = "Emilio Gomez Fernandez"
__copyright__ = "RISUM Project"

__version__ = "0.2"
__maintainer__ = "Emilio Gomez Fernandez"
__email__ = "emiliogf@altergeosistemas.com"
__status__ = "Development"
__date__ = "February, 2017"

from argparse import ArgumentParser
from pyspatialite import dbapi2 as db
from constants import HOME, SOFTWARE, BBOX, GTFS_DIR, GTFS_ODS, RELACIONES, TIEMPOS_PARADAS, OTP, OPENSHIFT_DIR
import os
import csv
import urllib
import sys
import linecache
import logging
import pygame
from subprocess import Popen, PIPE
from xml.dom import minidom
from colorama import Fore, init, Back
# Reinicializa colorama a sus estado original tras cada mensaje
init(autoreset=True)


def main():
    u"""Función centinela"""
  # try:
    parser = ArgumentParser(
        description='Genera un archivo GTFS estático para Santander', version='gtfs4sdr 1.0')
    parser.add_argument('-osm', action="store_true", default=False,
                        help='descarga nueva cartografia desde OpenStreetMap')
    parser.add_argument('-shp', action="store_true",
                        help='crea un archivo shapes.txt')
    parser.add_argument('-fv', action="store_true", default=False,
                        help='comprueba el archivo GTFS generado mediante FeedValidator')
    parser.add_argument('-sv', action="store_true", default=False,
                        help='comprueba el archivo GTFS generado mediante ScheduleViewer')
    parser.add_argument('-g', action="store_true", default=False,
                        help='genera el grafo para OpenTripPlanner')
    parser.add_argument('-ops', action="store_true", default=False,
                        help='sube el archivo Graph.obj generado a OpenShift')

    argumentos = parser.parse_args()
    shapes = argumentos.shp
    openstreetmap = argumentos.osm
    feedv = argumentos.fv
    schedulev = argumentos.sv
    grafo = argumentos.g
    openshift = argumentos.ops

    if openstreetmap is True:
        downloadOSM()

    importOSM()
    con = db.connect('/var/tmp/gtfs.sqlite')
    cursor = con.cursor()
    cursor.execute("DROP TABLE IF EXISTS relaciones")
    cursor.execute('CREATE TABLE relaciones (relacion INT, id TEXT);')
    con.commit()
    cursor.close()
    cargar_relaciones(RELACIONES)
    relaciones_lista = csv_orden_relaciones()
    import_orden_relaciones()
    sentidos_relaciones()
    ordenar_vias(relaciones_lista)
    convertir_geometria()
    ptos_rutas()
    calcular_distancia(relaciones_lista)
    excepciones()
    exportar_shape()
    # COMIENZA LA CONSTRUCCION DEL GTFS EXCEPTO LOS SHAPES
    exportar_calc(GTFS_ODS)
    exportar_calc(TIEMPOS_PARADAS)
    importar_csv()
    errores_excepciones()
    tiempos_paradas()
    ajuste_tiempos_paradas()
    tiempos_iguales()
    vista_stop_times()
    exportar_csv(GTFS_DIR)  # Exporta la vista final a csv

    # Elimina shapes.txt que esta vacío para susutituirlo por shapes_tmp.txt
    # que es el bueno y se renombra
    if os.path.isfile(GTFS_DIR + "shapes_tmp.txt") is True:
        print(Fore.GREEN + "AVISO:" + Fore.RESET +
              " Renombrando shape_tmp.txt -> shape.txt")
        os.system("rm " + GTFS_DIR + "shapes.txt")
        os.system("mv " + GTFS_DIR + "shapes_tmp.txt " +
                  GTFS_DIR + "shapes.txt")

    comprimir_txt(GTFS_DIR, HOME)  # Comprime los archivos
    if feedv is True:
        feedvalidator(GTFS_DIR)

    if schedulev is True:
        scheduleviewer(GTFS_DIR)

    if grafo is True:
        generar_grafo(OTP)

    if openshift is True:
        subir_grafo(OPENSHIFT_DIR, OTP)

    pygame.init()
    pygame.mixer.Sound(
        "/usr/bin/cvlc /usr/share/sounds/KDE-Sys-App-Positive.ogg").play()
    print (Back.GREEN + "¡Finalizado!" + Back.RESET)

  # except Exception:
    # PrintException()


def programas_necesarios(programas):
    u"""Verifica que están instalados los programas necesarios en el equipo."""
    for programa in programas:
        try:
            Popen([programa, '--help'], stdout=PIPE, stderr=PIPE)
        except OSError:
            msg = '¡ATENCIÓN! Este programa es necesario para ejecutar este script: {0}'.format(
                programa)
            sys.exit(msg)
    return


def downloadOSM():
    u"""Descarga la cartografía de OpenStreetMap para la región definida."""
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          " Descargando cartografía de OpenStreetMap para la envolvente '" + BBOX + "'.")
    os.system(
        "wget http://overpass-api.de/api/xapi_meta?*[bbox=" + str(BBOX) + "] -O /var/tmp/map.osm")
    return


def importOSM():
    u"""Importa la cartografia de OSM a una base de datos SQLite."""
    if fileexists('/var/tmp/map.osm', True) is False:
        sys.exit(Fore.RED + '¡Abortando ejecución!')
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          " Importando cartografía de OpenStreetMap en /var/tmp/gtfs.sqlite")
    removefile('/var/tmp/gtfs.sqlite')
    os.system("spatialite_osm_map -o /var/tmp/map.osm -d /var/tmp/gtfs.sqlite -m")


def cargar_relaciones(ruta_csv_relaciones):
    u"""Carga a la base de datos el csv "relaciones_rutas_transporte.csv" con las relaciones."""
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          " Importando el archivo CSV de relaciones de líneas de autobús")
    if fileexists(ruta_csv_relaciones, 'True') is False:
        sys.exit(Fore.RED + '¡Abortando ejecución!')

    con = db.connect('/var/tmp/gtfs.sqlite')
    cursor = con.cursor()
    cursor.execute("DROP TABLE IF EXISTS relaciones_rutas")
    cursor.execute(
        "CREATE TABLE relaciones_rutas (id TEXT, nombre TEXT, relacion INT);")
    reader = csv.reader(open(ruta_csv_relaciones, 'r'))
    for fila in reader:
        to_db = [unicode(fila[0], "utf8"), unicode(
            fila[1], "utf8"), unicode(fila[2], "utf8")]
        cursor.execute(
            "INSERT INTO relaciones_rutas (id, nombre, relacion) VALUES (?, ?, ?);", to_db)

    con.commit()
    cursor.close()
    return


def csv_orden_relaciones():
    u"""Ordena la vías que forman cada ruta.

    Analiza los XML de OSM para determinar el orden de las
    vías de cada relación y los exporta a un CSV.

    """
    con = db.connect('/var/tmp/gtfs.sqlite')
    cursor = con.cursor()
    # Al haber lineas que comparten la misma relación hay que seleccionar solo
    # los IDs unicos
    cursor.execute("SELECT DISTINCT(relacion) FROM relaciones_rutas;")
    relaciones = cursor.fetchall()
    relaciones_lista = []
    for fila in relaciones:
        # Volca el resultado de la consulta a una lista para utilizar en el
        # análisis del XML
        relaciones_lista.append(fila[0])
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          " Creándo el archivo /var/tmp/orden_relaciones.csv")

    # Crea primero un csv con una fila que servirá de cabecera
    with open("/var/tmp/orden_relaciones.csv", "wb") as archivo_texto:
        writer = csv.writer(archivo_texto, quoting=csv.QUOTE_NONE)
        writer.writerow(["relacion", "orden", "way"])

    # Analizo todas las relaciones y actualizo el csv
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          " Descarga y analiza los archivos XML de las relaciones de OSM")
    for r in relaciones_lista:
        lista = []

        print(Fore.GREEN + "AVISO:" + Fore.RESET +
              " Obteniendo el archivo: " + str(r) + ".xml de OpenStreetMap")
        url = 'http://api.openstreetmap.org/api/0.6/relation/' + str(r)
        urllib.urlretrieve(url, str(r) + ".xml")  # Descargamos el archivo.
        # Cargamos en objeto xmldoc el documento xml
        xmldoc = minidom.parse(str(r) + '.xml')
        itemlist = xmldoc.getElementsByTagName('member')

        for s in itemlist:
            if s.attributes['type'].value == "way":
                referencia = s.attributes['ref'].value
                lista.append(referencia)

                # Cargamos en la tabla 'relaciones' el id de las relaciones de OSM con la
                # referencia de la linea
                itemlist = xmldoc.getElementsByTagName('tag')

                for s in itemlist:
                    if s.attributes['k'].value == "ref":
                        referencia = s.attributes['v'].value
                        cursor.execute("INSERT INTO relaciones (relacion, id) VALUES (" +
                                       str(r) + ",'" + str(referencia) + "');")

                # Abro el csv creado y agrego nuevas filas con las relaciones
                with open("/var/tmp/orden_relaciones.csv", "a") as archivo_texto:
                    writer = csv.writer(archivo_texto, quoting=csv.QUOTE_NONE)
                    i = 1
                    for val in lista:
                        writer.writerow([r, i, val])
                        i = i + 1

                removefile(str(r) + ".xml")  # Se elimina el archivo xml

    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          " Se terminó de crear el archivo /var/tmp/orden_relaciones.csv con el orden de las relaciones.")
    con.commit()
    cursor.close()
    return(relaciones_lista)


def import_orden_relaciones():
    u"""Importa la tabla con el orden de las vías de cada relación en la base de datos."""
    con = db.connect('/var/tmp/gtfs.sqlite')
    cursor = con.cursor()
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          " Importando /var/tmp/orden_relaciones.csv en la base de datos /var/tmp/gtfs/gtfs.sqlite")
    cursor.execute("DROP TABLE IF EXISTS orden_relaciones")
    cursor.execute(
        "CREATE TABLE orden_relaciones (relacion INT, orden INT, way TEXT);")

    reader = csv.reader(open('/var/tmp/orden_relaciones.csv', 'r'))
    for fila in reader:
        to_db = [unicode(fila[0], "utf8"), unicode(
            fila[1], "utf8"), unicode(fila[2], "utf8")]
        cursor.execute(
            "INSERT INTO orden_relaciones (relacion, orden, way) VALUES (?, ?, ?);", to_db)

    con.commit()
    # TODO: El archivo orden_relaciones.csv contiene valores repetidos de cada
    # arco que se añaden a la tabla orden_relaciones.
    # Habría que ver por qué se generan. Mientra tanto lo borramos con la
    # siguiente SQL:
    cursor.execute(
        'DELETE FROM orden_relaciones WHERE rowid NOT IN (SELECT MIN(rowid) FROM orden_relaciones GROUP BY relacion, orden, way)')
    con.commit()
    cursor.close()
    return


def sentidos_relaciones():
    u"""Corrige la continuidad de las vías."""
    con = db.connect('/var/tmp/gtfs.sqlite')
    cursor = con.cursor()
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          " Corrigiendo la continuidad de las vías de cada ruta de autobús")
    # Creando tabla 'vias_rutas'
    cursor.execute("DROP TABLE IF EXISTS vias_rutas")
    cursor.execute('CREATE TABLE vias_rutas (id INTEGER PRIMARY KEY AUTOINCREMENT, relacion INT, orden INT, way TEXT, ROWID INTEGER, sub_type TEXT, name TEXT, Geometry NUM, coord_inicio TEXT, coord_fin TEXT);')

    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          " Ejecutando join entre tablas orden_relaciones <-> ln_highway")
    cursor.execute('INSERT INTO vias_rutas (relacion, orden, way, ROWID, sub_type, name, Geometry) SELECT a.relacion AS relacion, a.orden AS orden, a.way AS way, b.ROWID AS ROWID, b.sub_type AS sub_type, b.name AS name, b.Geometry AS Geometry FROM orden_relaciones AS a JOIN ln_highway AS b ON (a.way = b.id);')

    # Vias que estan en la tabla ln_railway
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          " Ejecutando join entre tablas orden_relaciones <-> ln_railway")
    cursor.execute('INSERT INTO vias_rutas (relacion, orden, way, ROWID, sub_type, name, Geometry) SELECT a.relacion AS relacion, a.orden AS orden, a.way AS way, b.ROWID AS ROWID, b.sub_type AS sub_type, b.name AS name, b.Geometry AS Geometry FROM orden_relaciones AS a JOIN ln_railway AS b ON (a.way = b.id);')

    cursor.execute(
        "UPDATE vias_rutas SET coord_inicio=ST_AsText(ST_StartPoint(Geometry)), coord_fin=ST_AsText(ST_EndPoint(Geometry));")
    con.commit()
    cursor.close()
    return


def ordenar_vias(relaciones_lista):
    u"""Revisa el orden de la vías."""
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          " Corrigiendo campos geométricos de arcos erróneos.")
    con = db.connect('/var/tmp/gtfs.sqlite')
    cursor = con.cursor()

    for m in relaciones_lista:
        z = 0
        y = 0
        error = True
        # Realizamos varias iteraciones sucesivas hasta que no haya ningún arco
        # incorrecto porque al modificar uno puede que surjan otros nuevos con
        # errores.
        while (error is True):
            y = y + 1
            sql = "SELECT a.id FROM vias_rutas a, vias_rutas b WHERE a.relacion=" + \
                str(m) + " AND b.relacion=" + str(m) + \
                " AND a.orden - 1 = b.orden AND a.coord_fin = b.coord_fin"
            cursor.execute(sql)
            arcos = cursor.fetchall()
            if len(arcos) != 0:  # Si no hay ningún arco erróneo cambiamos el interructor a false para que continúa con la siguiente relación
                for arco in arcos:
                    z = z + 1
                    sql = "UPDATE vias_rutas SET Geometry = ST_Reverse(Geometry), coord_inicio = ST_AsText(ST_StartPoint(ST_Reverse(Geometry))), coord_fin = ST_AsText(ST_EndPoint(ST_Reverse(Geometry))) WHERE id =" + str(
                        arco[0]) + ";"
                    cursor.execute(sql)
                    con.commit()
            else:
                error = False
            print ("Relación " + Fore.GREEN + str(m) + Fore.RESET + ": Iteración " +
                   str(y) + " --> " + Fore.GREEN + str(z) + Fore.RESET + " arcos invertidos.")
        print("")

    con.commit()
    cursor.close()
    return


def convertir_geometria():
    u"""Convierte la geometría multilínea en línea."""
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          " Convirtiendo la geometría multilínea a línea")
    con = db.connect('/var/tmp/gtfs.sqlite')
    cursor = con.cursor()
    cursor.execute('UPDATE vias_rutas SET Geometry=ST_LineMerge(Geometry);')
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          " Actualizando las columnas de coordenadas de inicio y fin de arco de la tabla 'vias_rutas'")
    # Actualiza las columnas coord_inicio y coord_fin.
    cursor.execute(
        "UPDATE vias_rutas SET coord_inicio=AsText(ST_StartPoint(Geometry)), coord_fin=ST_AsText(ST_EndPoint(Geometry));")
    con.commit()
    cursor.close()
    return


def ptos_rutas():
    u"""Extrae la geometría de los puntos de cada relación y añade un campo "orden".

    Crea una nueva tabla donde almacenar la geometria de puntos de cada linea.

    """
    print(Fore.GREEN + "AVISO:" + Fore.RESET + " Creando tabla 'shapes'")
    con = db.connect('/var/tmp/gtfs.sqlite')
    cursor = con.cursor()
    cursor.execute('DROP TABLE IF EXISTS shapes_tmp')
    cursor.execute('CREATE TABLE "shapes_tmp" (id INTEGER PRIMARY KEY AUTOINCREMENT, shape_id TEXT, relacion TEXT, shape_pt_lon REAL, shape_pt_lat REAL, shape_pt_sequence INT, shape_dist_traveled INT);')
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          " Extrayendo nodos de cada ruta")
    cursor.execute("SELECT id FROM vias_rutas;")
    rs = cursor.fetchall()

    # Bucle para recorrer el contenido de la lista
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          " Almacenando geometria de puntos de cada ruta")
    grupo = ""
    secuencia = 1
    for i in rs:
        # Indica el numero de nodos que componen la linea
        cursor.execute(
            "SELECT ST_NPoints(Geometry), relacion FROM vias_rutas WHERE id =" + str(i[0]) + ";")
        ptos = cursor.fetchone()
        for z in range(1, int(ptos[0])):
            if grupo != ptos[1]:
                grupo = ptos[1]
                secuencia = 1
            else:
                secuencia = secuencia + 1
            # Inserta en la nueva tabla cada punto de cada geometria
            cursor2 = con.cursor()
            sql = ("INSERT INTO shapes_tmp(relacion, shape_pt_lon, shape_pt_lat, shape_pt_sequence) "
                   "SELECT relacion, ST_X(ST_PointN(Geometry," + str(
                       z) + ")) AS shape_pt_lon, ST_Y(ST_PointN(Geometry," + str(z) + ")) AS shape_pt_lat, " + str(secuencia) +
                   " FROM vias_rutas WHERE id =" + str(i[0]) + " AND shape_pt_lon IS NOT NULL;")
            cursor2.execute(sql)
    con.commit()
    cursor.close()
    cursor2.close()
    return


def calcular_distancia(relaciones_lista):
    u"""Calcula la distancia de cada arco de la ruta y el recorrido total."""
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          " Calculando la distancia entre puntos de cada ruta.")
    con = db.connect('/var/tmp/gtfs.sqlite')
    cursor = con.cursor()
    cursor.execute("DROP TABLE IF EXISTS shapes")
    cursor.execute("DROP VIEW IF EXISTS distancia_tmp")
    sql = ("CREATE VIEW distancia_tmp AS "
           "SELECT b.id, ST_Distance(ST_Transform(ST_PointFromText('POINT('|| a.shape_pt_lat ||' '|| a.shape_pt_lon ||')', 4326), 3857), "
           "ST_Transform(ST_PointFromText('POINT('|| b.shape_pt_lat ||' '|| b.shape_pt_lon ||')', 4326),3857)) AS distancia_3857 "
           "FROM shapes_tmp AS a, shapes_tmp AS b WHERE a.relacion = b.relacion  AND a.shape_pt_sequence = b.shape_pt_sequence - 1 ORDER BY a.id ASC;")
    cursor.execute(sql)
    sql = ("CREATE TABLE shapes AS "
           "SELECT a.id AS id, a.relacion AS relacion, a.shape_pt_lon AS shape_pt_lon, a.shape_pt_lat AS shape_pt_lat, a.shape_pt_sequence AS shape_pt_sequence, "
           "b.distancia_3857 AS shape_dist_traveled FROM shapes_tmp AS a LEFT JOIN distancia_tmp AS b USING (id) ORDER BY a.id")
    cursor.execute(sql)

    # Elimina registro duplicados porque hay relaciones repetidas por el id de
    # viajes para invierno y verano, que tienen la misma relacion
    # TODO: probablemente ya no haga falta al seleccionar los ID distintos
    print(Fore.GREEN + "AVISO:" + Fore.RESET + " Eliminando arcos duplicados.")
    cursor.execute(
        "DELETE FROM shapes WHERE rowid NOT IN (SELECT min(rowid) FROM shapes GROUP BY id);")
    cursor.execute(
        "UPDATE shapes SET shape_dist_traveled = 0 WHERE shape_dist_traveled IS NULL;")
    con.commit()
    # Suma las distancias correlativamente
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          " Sumando distancias correlativas entre arcos.")
    for m in relaciones_lista:
        cursor.execute("SELECT id, shape_dist_traveled FROM shapes WHERE relacion = " +
                       str(m) + " ORDER BY id ASC;")
        puntos = cursor.fetchall()
        distancia = 0
        for registros in puntos:
            distancia = distancia + int(registros[1])
            cursor.execute("UPDATE shapes SET shape_dist_traveled =" +
                           str(distancia) + " WHERE id =" + str(registros[0]) + ";")
        print("Relación: " + str(m) + " --> " + str(distancia) + " m.")
    con.commit()
    cursor.close()
    return


def excepciones():
    u"""Introduce excepciones para preparar los datos para su exportación."""
    con = db.connect('/var/tmp/gtfs.sqlite')
    cursor = con.cursor()
    # Crea una vista para organizar los campos que deseo exportar
    cursor.execute('DROP TABLE IF EXISTS shapes_csv')
    sql = ("CREATE TABLE shapes_csv AS SELECT b.id AS shape_id, a.shape_pt_lon AS shape_pt_lon, a.shape_pt_lat AS shape_pt_lat, "
           "a.shape_pt_sequence AS shape_pt_sequence, a.shape_dist_traveled AS shape_dist_traveled "
           "FROM shapes AS a JOIN relaciones_rutas AS b USING (relacion) ORDER BY b.id, a.shape_pt_sequence")
    cursor.execute(sql)
    # Lineas de vuelta de los ferrocarriles
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          " Generando líneas de vuelta de los ferrocarriles.")
    ferrocarriles = ["FEVE-S1", "FEVE-S2",
                     "FEVE-S2-1", "FEVE-S2-2", "RENFE-C1"]
    for linea in ferrocarriles:
        distancia = 0
        sql = "SELECT * FROM shapes_csv WHERE shape_id = '" + \
            str(linea) + "' ORDER BY shape_pt_sequence DESC LIMIT 1"
        cursor.execute(sql)
        tramos = cursor.fetchone()
        dist_max = tramos[4]
        secuencia = int(tramos[3])
        print("Invirtiendo secuencia " + Fore.GREEN +
              str(linea) + Fore.RESET + " --> " + Fore.GREEN + str(tramos[4]) + Fore.GREEN + " puntos.")
        id_shape = linea + "-V"

        # Primer punto con distancia cero
        cursor.execute("SELECT * FROM shapes_csv WHERE shape_id = '" + str(linea) +
                       "' AND shape_pt_sequence = " + str(secuencia) + ";")
        tramo = cursor.fetchone()
        cursor.execute("INSERT INTO shapes_csv(shape_id, shape_pt_lon, shape_pt_lat, shape_pt_sequence, shape_dist_traveled) VALUES ('" +
                       str(id_shape) + "', " + str(tramo[1]) + ", " + str(tramo[2]) + ", 1, 0);")

        for z in range(1, int(tramos[3])):
            # Obtengo un tramo y el anterior para poder calcular la distancia
            # del primero
            cursor.execute("SELECT * FROM shapes_csv WHERE shape_id = '" +
                           str(linea) + "' AND shape_pt_sequence = " + str(secuencia) + ";")
            tramo = cursor.fetchone()
            # print("Secuencia: " + str(secuencia))
            cursor.execute("SELECT * FROM shapes_csv WHERE shape_id = '" +
                           str(linea) + "' AND shape_pt_sequence = " + str(secuencia - 1) + ";")
            anterior_tramo = cursor.fetchone()
            distancia = distancia + (int(tramo[4]) - int(anterior_tramo[4]))
            # print("Distancia:" + str(distancia))
            cursor.execute("INSERT INTO shapes_csv(shape_id, shape_pt_lon, shape_pt_lat, shape_pt_sequence, shape_dist_traveled) VALUES ('" + str(
                id_shape) + "', " + str(anterior_tramo[1]) + ", " + str(anterior_tramo[2]) + ", " + str(z + 1) + ", " + str(distancia) + ");")
            secuencia = secuencia - 1

        # Ñapa para que aparezca el ultimo punto, que si no no aparecia.
        cursor.execute("SELECT * FROM shapes_csv WHERE shape_id = '" +
                       str(linea) + "' ORDER BY shape_pt_sequence ASC LIMIT 1")
        tramos = cursor.fetchone()
        z = z + 1

    print(Fore.GREEN + "¡Secuencias " + str(ferrocarriles) + " invertidas!")
    con.commit()
    cursor.close()
    return


def exportar_shape():
    u"""Exportar la tabla shapes_csv a CSV shapes.txt."""
    archivo = GTFS_DIR + 'shapes_tmp.txt'
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          "Exportando las geometrías a " + archivo)
    direxists(GTFS_DIR)
    os.system('/usr/bin/sqlite3 -header -csv "/var/tmp/gtfs.sqlite" "SELECT shape_id, shape_pt_lat, shape_pt_lon, shape_pt_sequence, shape_dist_traveled FROM shapes_csv ORDER BY shape_id, shape_pt_sequence;" > "' + archivo + '"')
    return


def exportar_calc(hoja):
    u"""Export las hojas de cálculo ods."""
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          "Exportando el libro de cálculo " + hoja + "a " + GTFS_DIR + "*.txt")
    os.system('/usr/bin/ssconvert -S --export-type=Gnumeric_stf:stf_csv "' +
              hoja + '" "' + GTFS_DIR + '%s.txt"')
    return


def importar_csv():
    u"""Importa las hojas de cálculo csv a la base de datos."""
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          "Importando archivos .txt provenientes del archivo .ods en la base de datos.")
    os.system('/usr/bin/sqlite3 /var/tmp/gtfs.sqlite < "' + HOME + 'tables.sql"')
    contenido = ".separator ','"
    contenido = contenido + '\n.import ' + GTFS_DIR + "agency.txt agency"
    contenido = contenido + '\n.import ' + GTFS_DIR + "calendar.txt calendar"
    contenido = contenido + '\n.import ' + GTFS_DIR + \
        "calendar_dates.txt calendar_dates\n"
    contenido = contenido + '\n.import ' + GTFS_DIR + \
        "fare_attributes.txt fare_atributes"
    contenido = contenido + '\n.import ' + GTFS_DIR + "fare_rules.txt fare_rules"
    contenido = contenido + '\n.import ' + GTFS_DIR + "frequencies.txt frequencies"
    contenido = contenido + '\n.import ' + GTFS_DIR + "routes.txt routes"
    contenido = contenido + '\n.import ' + GTFS_DIR + "stops.txt stops"
    contenido = contenido + '\n.import ' + GTFS_DIR + "stop_times.txt stop_times"
    contenido = contenido + '\n.import ' + GTFS_DIR + "trips.txt trips"
    contenido = contenido + '\n.import ' + GTFS_DIR + \
        "tiempos_paradas.txt tiempos_paradas"
    f = open(HOME + 'gtfs_sheets.sql', 'w')
    f.write(contenido)
    f.close()
    os.system('sqlite3 /var/tmp/gtfs.sqlite < "' + HOME + 'gtfs_sheets.sql"')

    # Elimina la primera fila porque al importar mete el nombre de la columna.
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          "Eliminando para cada tabla la primera fila que contiene el nombre de las columnas.")
    con = db.connect('/var/tmp/gtfs.sqlite')
    cursor = con.cursor()
    tablas = ['agency', 'calendar', 'calendar_dates', 'fare_atributes', 'fare_rules',
              'frequencies', 'routes', 'stops', 'stop_times', 'trips', 'tiempos_paradas']
    for tabla in tablas:
        sql = "DELETE FROM " + tabla + " WHERE ROWID = 1"
        cursor.execute(sql)

    # Por si acaso hay algún error en la tabla 'tiempos_paradas' con alguna ruta cuya primera parada
    # por error no tenga correctamente puesta la salida en el 00:00:00 (se han
    # corregido pero por si acaso)
    sql = ("UPDATE tiempos_paradas SET tiempo = '00:00:00', toriginal = '00:00:00', calculo = '00:00:00' "
           "WHERE secuencia = 1 and tiempo <> '00:00:00'")
    cursor.execute(sql)
    if cursor.rowcount > 0:
        print(Fore.CYAN + "AVISO:" + Fore.RESET + "Se han corregido " + Fore.CYAN + str(cursor.rowcount) + Fore.RESET +
              " líneas de la tabla 'tiempos_paradas' cuya primera parada no tiene el tiempo 00:00:00")
    con.commit()
    cursor.close()
    return


def errores_excepciones():
    u"""Corrección de errores y excepciones de tiempos de paradas en rutas."""
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          "Comprobando posibles errores en la tabla 'stop_times'")
    con = db.connect('/var/tmp/gtfs.sqlite')
    cursor = con.cursor()
    cursor.execute(
        "SELECT trip_id FROM stop_times GROUP BY trip_id HAVING count(*) > 1 ORDER BY trip_id ASC;")
    registro = cursor.fetchall()
    if registro is None:
        print(Fore.RED + "ADVERTENCIA: Registros duplicados: " + ', '.join(registro))
        sys.exit()
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          "Corrigiendo excepciones en 'stop_times.txt'")
    os.system('/usr/bin/sqlite3 "/var/tmp/gtfs.sqlite" < "' +
              HOME + 'exceptions.sql"')
    con.commit()
    cursor.close()
    return


def tiempos_paradas():
    u"""Inserta en la tabla 'stop_times' los horarios de paradas para cada línea"""
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          "Insertarndo en la tabla 'stop_times' los horarios de pasos por parada para cada línea.")
    con = db.connect('/var/tmp/gtfs.sqlite')
    cursor = con.cursor()
    sql = ("INSERT INTO stop_times(trip_id, arrival_time, departure_time, stop_id, stop_sequence, id_tiempos) "
           "SELECT s.trip_id, "
           "TIME(strftime('%s', s.arrival_time) + strftime('%s',t.tiempo) ,'unixepoch') AS arrival_time, "
           "TIME(strftime('%s', s.departure_time) + strftime('%s',t.tiempo) ,'unixepoch') AS departure_time, "
           "t.parada, "
           "t.secuencia, "
           "s.id_tiempos "
           "FROM stop_times AS s "
           "INNER JOIN  tiempos_paradas AS t "
           "WHERE s.id_tiempos = t.id_tiempos")
    cursor.execute(sql)
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          "Eliminando de la tabla 'stop_times' horarios repetidos.")  # Esto ocurre porque la parada de cabecera aparece dos veces.
    sql = ('DELETE FROM stop_times WHERE rowid NOT IN ('
           'SELECT MIN(rowid) FROM stop_times GROUP BY trip_id, arrival_time, departure_time, stop_id, stop_sequence)')
    cursor.execute(sql)
    con.commit()
    cursor.close()
    return


def ajuste_tiempos_paradas():
    u"""Ajusta el tiempo de las paradas cuando el tiempo de recorrido de un línea supera las 00:00:00."""
    # raw_input("Parado!")
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          "Corrigiendo horarios de paso por parada más alla de las 00:00:00 de la tabla 'stop_times'.")
    con = db.connect('/var/tmp/gtfs.sqlite')
    cursor = con.cursor()
    sql = ("UPDATE stop_times "
           "SET arrival_time = (strftime('%H', arrival_time) + 24)  || ':' || strftime('%M', arrival_time) || ':' || strftime('%S', arrival_time), "
           "departure_time = (strftime('%H', departure_time) + 24)  || ':' || strftime('%M', departure_time) || ':' || strftime('%S', departure_time) "
           "WHERE trip_id  NOT IN "
           "(SELECT trip_id FROM stop_times WHERE stop_sequence = 1 AND arrival_time BETWEEN '00:00:00' AND '05:59:59' GROUP BY  trip_id)"
           " AND stop_sequence > 1 AND  arrival_time BETWEEN '00:00:00' AND '05:59:59'")

    cursor.execute(sql)
    con.commit()
    cursor.close()
    return


def tiempos_iguales():
    u"""Revisa que paradas en un mismo viaje tienen la misma hora y estan seguidas, para corregir el tiempo añadiendo segundos y que no de error."""
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          "Ajustando tiempos entre paradas con mismo horario.")
    con = db.connect('/var/tmp/gtfs.sqlite')
    cursor = con.cursor()
    sql = "SELECT DISTINCT trip_id FROM stop_times"
    cursor.execute(sql)
    viajes = cursor.fetchall()
    for v in viajes:
        tiempo = 0
        cursor.execute("SELECT trip_id, arrival_time, COUNT(trip_id) AS repe FROM stop_times WHERE trip_id = '" +
                       v[0] + "' GROUP BY arrival_time HAVING count(*) > 1;")
        viaje = cursor.fetchall()
        for registros in viaje:
            print registros[0]
            cursor.execute("SELECT trip_id, arrival_time, stop_sequence FROM stop_times WHERE stop_sequence NOT IN (SELECT MIN(stop_sequence) FROM stop_times WHERE trip_id = '" +
                           registros[0] + "' AND arrival_time = '" + registros[1] + "') AND trip_id = '" + registros[0] + "' AND arrival_time = '" + registros[1] + "'")
            horario = cursor.fetchall()
            for hora in horario:
                # Reparte los segundos de salida en el mismo minuto entre las
                # diferentes paradas, excepto la primera que se queda como
                # esta.
                tiempo = tiempo + 59 / int(registros[2])
                print (Fore.GREEN + str(hora[0]) + Fore.RESET + " --> secuencia: " + Fore.GREEN + str(hora[2]) + Fore.RESET + " --> " + Fore.GREEN + str(
                    hora[1]) + Fore.RESET + " --> tiempo: " + Fore.GREEN + str(tiempo))
                sql = ("UPDATE stop_times SET arrival_time = strftime('%H:%M:%S', DATETIME(arrival_time, '+" + str(tiempo) +
                       " seconds')), departure_time = strftime('%H:%M:%S', DATETIME(arrival_time, '+" + str(tiempo) + " seconds')) WHERE trip_id = '" + str(hora[0]) + "' AND stop_sequence =" + str(hora[2]))
                cursor.execute(sql)
                tiempo = 0
    con.commit()
    cursor.close()
    return


def vista_stop_times():
    u"""Crea una nueva vista con los viajes ordenados segun identificador y secuencia de parada"""
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          " Realizando copia en la vista 'stop_times_orden'")
    con = db.connect('/var/tmp/gtfs.sqlite')
    cursor = con.cursor()
    sql = ("CREATE VIEW stop_times_orden AS "
           "SELECT trip_id, arrival_time, departure_time, stop_id, stop_sequence, stop_headsign, pickup_type, drop_off_time, shape_dist_traveled "
           "FROM stop_times ORDER BY trip_id, stop_sequence")
    cursor.execute(sql)
    con.commit()
    cursor.close()
    con.close()
    return


def exportar_csv(GTFS_DIR):
    u"""Exporta la tablas 'stop_times_orden' y 'trips' a csv."""
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          "Exportando en la tabla 'stop_times' a " + GTFS_DIR + "stop_times.txt")
    os.system('sqlite3 -header -csv /var/tmp/gtfs.sqlite "SELECT * FROM stop_times_orden;" > ' +
              GTFS_DIR + 'stop_times.txt')
    # Exporta de nuevo trips.txt para generar un csv sin la columna horario
    # que sobre (en SQLITE no existe DROP COLUMN para hacerlo)
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          "Exportando en la tabla 'trips' a " + GTFS_DIR + "trips.txt")
    sql = ("SELECT route_id, service_id, trip_id, trip_headsign, direction_id, block_id, shape_id, wheelchair_accessible "
           "FROM trips;")
    os.system('sqlite3 -header -csv /var/tmp/gtfs.sqlite "' +
              sql + '" > ' + GTFS_DIR + 'trips.txt')
    return


def comprimir_txt(GTFS_DIR, HOME):
    u"""Comprime los archivos csv para generar el archivo gtfs.zip."""
    removefile(GTFS_DIR + 'tiempos_paradas.txt')
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          "Comprimiento los archivos *.txt a /var/tmp/gtfs/gtfs.zip.")
    comando = 'cd "' + GTFS_DIR + '"; zip -r gtfs.zip *.txt'
    os.system(comando)
    print(Fore.GREEN + "AVISO:" + Fore.RESET +
          "Comprimiento los archivos *.txt a " + OTP + "cache/gtfs/gtfs.zip.")
    comando = 'cd "' + GTFS_DIR + '"; zip -r "' + OTP + 'cache/gtfs/gtfs.zip" *.txt'
    # feedvalidator.py "/var/tmp/gtfs/gtfs.zip" --output=CONSOLE >>
    # "/var/tmp/feedvalidator.log"
    os.system(comando)
    return


def feedvalidator(GTFS_DIR):
    u"""Validar archivo con feedvalidator."""
    print("Lanzando FeedValidator..")
    comando = 'feedvalidator.py "' + GTFS_DIR + \
        'gtfs.zip" --output=CONSOLE > "/var/tmp/feedvalidator.log"'
    print comando
    os.system(comando)
    return


def scheduleviewer(GTFS_DIR):
    u"""Valida el archivo GTFS generado con ScheduleViewer."""
    print("Ejecutando ScheduleViewer...")
    comando = 'schedule_viewer.py "' + GTFS_DIR + 'gtfs.zip"'
    print (comando + " | xdg-open http://localhost:8765")
    os.system(comando + " | xdg-open http://localhost:8765")
    return


def generar_grafo(OTP):
    u"""Generar el grafo necesario para OpenTripPlanner."""
    print "Copiando el archivo 'map.osm' a " + OTP + "cache/osm/map.osm"
    comando = 'cp /var/tmp/map.osm "' + OTP + '/cache/osm/map.osm"'
    os.system(comando)
    print("Generando grafo...")
    comando = '"' + OTP + 'bin/build-graph.sh"'
    print comando
    os.chdir(OTP)
    os.system(comando + "| tee /var/tmp/grafo.log")
    print "Generado el archivo de registro '/var/tmp/grafo.log' en el directorio " + OTP


def subir_grafo(directorio_ftp_grafo, ruta_otp):
    u"""Sube el grafo a la instancia OpenShift de SantanderGo!."""
    print "Subiendo 'Graph.obj' a " + directorio_ftp_grafo
    comando = '/usr/bin/scp "' + ruta_otp + \
        'Graph.obj" ' + directorio_ftp_grafo + 'Graph.obj'
    os.system(comando)
    print "Grafo subido!"
    os.system("/usr/bin/rhc app restart -a santandergo")


def removefile(target_file):
    u"""Elimina el archivo si existe."""
    if os.path.isfile(target_file):
        os.remove(target_file)
        print ('Eliminado ' + Fore.CYAN + target_file)
    return


def fileexists(path, msg):
    u"""Indica si un archivo ya existe o no."""
    if os.path.isfile(path):
        if msg is True:
            print (Fore.CYAN + 'ADVERTENCIA: Ya existe el archivo ' + path)
            return True
    else:
        if msg is True:
            print (Fore.YELLOW + 'ADVERTENCIA: No existe el archivo ' + path)
            return False


def direxists(path):
    u"""Crea el directorio si este no existe."""
    if not os.path.exists(path):
        print('No existe el directorio ' + Fore.RED +
              path + Fore.RESET + '. Creándolo.')
        os.makedirs(path)
    return


def telegram(mensaje):
    u"""Sends a message to a Telegram bot warning that an error has occurred in the program."""
    mensaje = mensaje.replace(
        '"', '')  # Reemplaza las comillas dobles  para que no de error al ejecutar el comando en bash.
    comando = '''/usr/local/bin/telegram-send "''' + mensaje + '''"'''
    os.system(comando)
    return


def PrintException():
    u"""Imprime por pantalla excepciones de error."""
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    excepcion = '''EXCEPCION EN ({}, LINEA {} "{}"): {}'''.format(
        filename, lineno, line.strip(), exc_obj)
    print 'EXCEPCION EN ({}, LINEA {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)
    logging.exception(excepcion)
    # Reemplaza las comillas dobles  para que no de error al ejecutar el
    # comando en bash.
    excepcion = excepcion.replace('"', '')
    # telegram(excepcion) #Envía mensaje de aviso de la excepción por Telegram
    return


if __name__ == "__main__":
    programas_necesarios(SOFTWARE)
    main()

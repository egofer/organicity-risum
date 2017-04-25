#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Genera feeds GTFS en tiempo real a partir de datos de la empresa de autobuses TUS
Requiere los paquetes Python:
pip install flask requests python-dateutil --no-no-cache-dir
pip freeze
'''

__author__ = "Emilio Gomez Fernandez"
__copyright__ = "Copyright 2016, Emilio Gomez Fernandez"

__version__ = "0.1"
__maintainer__ = "Emilio Gomez Fernandez"
__email__ = "emiliogf@altergeosistemas.com"
__status__ = "Development"
__date__ = "Noviembre de 2016"

import os
import gtfs_realtime_pb2 as gtfsrtpb
import time
import io
import json
import requests
import dateutil.parser
from datetime import datetime
from google.protobuf import text_format
from flask import Flask, send_file, make_response, abort, request
from argparse import ArgumentParser

app = Flask(__name__)

VEHICLES_POSITIONS = 'http://datos.santander.es/api/rest/datasets/control_flotas_posiciones.json'
TRIP_UPDATES = 'http://datos.santander.es/api/rest/datasets/control_flotas_estimaciones.json'

#Feed Header
def buildHeader():
    fm = gtfsrtpb.FeedMessage()
    fh = fm.header
    fh.gtfs_realtime_version = "1.0"
    fh.incrementality = 0  # Determina si la búsqueda actual es incremental (valor por defecto).
    fh.timestamp = int(time.mktime(datetime.now().timetuple()))  # Momento en que se creó el contenido de este feed (en tiempo del servidor). En tiempo UNIX.
    return fm

#Feed Vehicle Positions
def buildVehiclePosition():
    r = requests.get(VEHICLES_POSITIONS)
    data = r.json()

    fm = buildHeader()
    for item in data['resources']:

        timez = dateutil.parser.parse(item['ayto:instante']) #Hora UTC

        fe = fm.entity.add()
        fe.id = 'vehicle_position_' + str(item['ayto:vehiculo'])

        fe.vehicle.trip.trip_id = str(item['ayto:servicio']) #¡OJO! REVISAR: El trip_id del feed GTFS al cual hace referencia este selector.

        fe.vehicle.trip.schedule_relationship = 0 #SCHEDULED: Viaje que se está ejecutando de acuerdo con su programa de GTFS (lo suficientemente parecido a él).
        fe.vehicle.trip.route_id = 'TUS-' + str(item['ayto:linea']) #Se ajusta el route_id al identificador del GTFS añadiendo el prefijo 'TUS-'

        fe.vehicle.timestamp = int(time.mktime(timez.timetuple())) #Momento en el cual se midió la posición del autobús. En tiempo UNIX.
        fe.vehicle.vehicle.id = str(item['ayto:vehiculo']) #Identificación interna del sistema para el autobus.
        fe.vehicle.vehicle.label = str(item['ayto:coche']) #Etiqueta visible para el usuario que se debe mostrar al pasajero para ayudarlo a identificar el bus.
        fe.vehicle.position.latitude = float(item['wgs84_pos:lat']) #Latitud en sistema de coordenadas WGS-84 (EPSG:4326).
        fe.vehicle.position.longitude = float(item['wgs84_pos:long']) #Longitud en sistema de coordenadas WGS-84 (EPSG:4326).
        fe.vehicle.position.speed = float(item['ayto:velocidad'])*1000/3600 #Velocidad del bus en m/s
        fe.vehicle.congestion_level = 0 #Nivel de congestión del tráfico.
        fe.vehicle.current_status = 2 #El vehículo ha partido y está en tránsito hacia la siguiente parada (valor por defecto). ¿Se puede inferir de "ayto:estado"?

    return fm

#Feed Trip Updates
def buildTripUpdate():
    r = requests.get(TRIP_UPDATES)
    data = r.json()

    fm = buildHeader()
    for item in data['resources']:
        timez = dateutil.parser.parse(item['ayto:fechActual']) #Hora UTC
        fe = fm.entity.add()

        fe.id = 'trip_update_' + str(item['ayto:etiqLinea']) + '_' + str(item['dc:identifier']) #¡OJO! No tenemos el ID del vehículo pero es opcional


        #Las líneas 17 y 18 tienes recorridos e id_route diferentes según horario pero esto no se recoge en el
        #feed de Santander Datos Abiertos, por lo que hay que determinarlo a través del conteniedo del item 'ayto:destino1'
        destination = item['ayto:destino1'].encode('utf-8').lower()

#         fe.trip_update.trip.trip_id = 'TUS-2-INV-O-LI-COR1722GES' #'TUS-2-INV-SI-COR1814GES'#item['ayto:destino1'].encode('utf-8')

        if str(item['ayto:etiqLinea']) == '17' and destination.find('bº la torre') == -1:
            fe.trip_update.trip.route_id = 'TUS-' + str(item['ayto:etiqLinea']) + '-1'
        elif str(item['ayto:etiqLinea']) == '17' and destination.find('bº la torre') != -1:
            fe.trip_update.trip.route_id = 'TUS-' + str(item['ayto:etiqLinea']) + '-2'
        elif str(item['ayto:etiqLinea']) == '18' and destination.find('por corbanera') != -1:
            fe.trip_update.trip.route_id = 'TUS-' + str(item['ayto:etiqLinea']) + '-1'
        elif str(item['ayto:etiqLinea']) == '18' and destination.find('por corbanera') == -1:
           fe.trip_update.trip.route_id = 'TUS-' + str(item['ayto:etiqLinea'])  + '-2'
        else:
            fe.trip_update.trip.route_id = 'TUS-' + str(item['ayto:etiqLinea'])

        stu = fe.trip_update.stop_time_update.add()
        stu.arrival.time = int(time.mktime(timez.timetuple())) + int(item['ayto:tiempo1']) #Tiempo UNIX estimado de llegada.
        stu.stop_id = str(item['ayto:paradaId'])

        fe.trip_update.vehicle.label = str(item['ayto:etiqLinea'])

    return fm


@app.route('/')
def home():
    html = '<p style="text-align: right;"><small>' + str(datetime.now()) + '</small></p>'
    html = html + '''<h1>RISUM Project</h1>
<p>Real-time Information for a Seamless Urban Mobility (<a href="https://risum.altergeosistemas.com">RISUM</a>) aims to enhance intermodal transport through the combined use of the public urban transport in the city of Santander. This service provide real-time public transport information under the GTFS standard, making public transit data readily available so developers can consume the data to build applications that simplify navigating transit systems. Therefore, results will provide the foundations of possible future actions in relation to the Urban Mobility Challenge to be addressed in the city.</p>
<p><span id="result_box" class="" lang="en"><span class="">RISUM is an experiment developed within the European Union's&nbsp;<a href="http://organicity.eu/">Organicity</a> project bringing together three smart cities: <a href="http://osm.org/go/0H9bk-?m=">Aarhus</a>, <a href="http://osm.org/go/euu4g-?m=">London</a>, <a href="http://osm.org/go/b~Nxp-?m=">Santander</a>.</span></span></p>
<p>This project has received funding from the European Union&rsquo;s Horizon 2020 research and innovation programme under grant agreement No 645198.</p>
<h2>GTFS Realtime feeds</h2>
<p>Here's example links to view the information in the plain text debugging format:</p>
<ul>
<li><a href="http://gtfs-altergeo.rhcloud.com/trip-updates/debug">http://gtfs-altergeo.rhcloud.com/trip-updates/debug</a>&nbsp;- For estimate arrival time updates</li>
<li><a href="http://gtfs-altergeo.rhcloud.com/vehicle-positions/debug">http://gtfs-altergeo.rhcloud.com/vehicle-positions/debug</a>&nbsp;- For vehicle positions</li>
</ul>
<p>And Protocol Buffer Format (more smaller and faster, should be used by apps):</p>
<ul>
<li><a href="http://gtfs-altergeo.rhcloud.com/trip-updates">http://gtfs-altergeo.rhcloud.com/trip-updates</a>&nbsp;- For estimate arrival time updates</li>
<li><a href="http://gtfs-altergeo.rhcloud.com/vehicle-positions">http://gtfs-altergeo.rhcloud.com/vehicle-positions</a>&nbsp;- For vehicle positions</li>
</ul>'''

    return html


@app.route('/vehicle-positions')
def feedVehiclePosition():
    return send_file(io.BytesIO(buildVehiclePosition().SerializeToString()))


@app.route('/vehicle-positions/debug')
def debugFeedVehiclePosition():
    feedjson = text_format.MessageToString(buildVehiclePosition())
    response = make_response(feedjson)
    response.headers['Content-Type'] = 'text/plain'
    return response


@app.route('/trip-updates')
def feedTripUpdate():
    return send_file(io.BytesIO(buildTripUpdate().SerializeToString()))


@app.route('/trip-updates/debug')
def debugFeedTripUpdate():
    feedjson = text_format.MessageToString(buildTripUpdate())
    response = make_response(feedjson)
    response.headers['Content-Type'] = 'text/plain'
    return response


@app.route('/callback')
def Organicitycallback():
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    state = request.args.get('state', '')
    if not is_valid_state(state):
        # Uh-oh, this request wasn't started by us!
        abort(403)
    code = request.args.get('code')
    print code
    # We'll change this next line in just a moment
    return "got a code! %s" % code


if __name__ == "__main__":
        #host = os.environ['OPENSHIFT_PYTHON_IP']
        #port = int(os.environ['OPENSHIFT_PYTHON_PORT'])

    if 'OPENSHIFT_PYTHON_IP' in os.environ:
        from wsgiref.simple_server import make_server
        httpd = make_server('OPENSHIFT_PYTHON_IP', 8051, app)
        # Wait for a single request, serve it and quit.
        #httpd.handle_request()
        # Respond to requests until process is killed
        httpd.serve_forever()
    else:
        app.run(debug=True)

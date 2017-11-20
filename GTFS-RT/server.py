#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Generate real-time GTFS feeds from TUS bus company data
In OpenShift you may require the parameter --no-cache-dir:
pip install paquete --no-cache-dir
pip freeze
'''

__author__ = "Emilio Gomez Fernandez"
__copyright__ = "Copyright 2017, Emilio Gomez Fernandez"

__version__ = "0.5"
__maintainer__ = "Emilio Gomez Fernandez"
__email__ = "emiliogf@altergeosistemas.com"
__status__ = "Development"
__date__ = "Marzo de 2017"

import os
import gtfs_realtime_pb2 as gtfsrtpb
import time
import io
import dateutil.parser
import sqlite3
import pytz
import datetime
from google.protobuf import text_format
from flask import Flask, send_file, make_response, abort, request
from argparse import ArgumentParser

DIR_TMP = '/tmp/'
# DIR_TMP = os.environ["OPENSHIFT_TMP_DIR"]
DIR_TMP = os.environ["OPENSHIFT_DATA_DIR"]
app = Flask(__name__)

# Feed Header

def buildHeader():
    fm = gtfsrtpb.FeedMessage()
    fh = fm.header
    fh.gtfs_realtime_version = "0.5"
    # Determines whether the current search is incremental (default value).
    fh.incrementality = 0
    # Time when the content of this feed was created (in server time). 
    # In UNIX time.
    fh.timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
    return fm


def buildVehiclePosition():
    """Build a GTFS real-time feed on the position of TUS buses"""

    con = sqlite3.connect(DIR_TMP + 'bustus.sqlite')
    cursor = con.cursor()
    sql = """SELECT trip_id,
        "ayto:instante",
        "ayto:vehiculo",
        "ayto:servicio",
        "ayto:linea",
        "ayto:coche",
        "wgs84_pos:lat",
        "wgs84_pos:long",
        "ayto:velocidad"
        FROM posicion_vehiculos"""
    cursor.execute(sql)
    vehiculos = cursor.fetchall()
    fm = buildHeader()
    for item in vehiculos:
        timez = dateutil.parser.parse(item[1])  # UTC Time ('ayto:instante')
        fe = fm.entity.add()
        fe.id = 'vehicle_position_' + str(item[2])

        #  Trip ID (' trip_id').
        fe.vehicle.trip.trip_id = str(item[0])
        # SCHEDULED: Trip that is running according to its GTFS schedule
        # (sufficiently similar to it).
        fe.vehicle.trip.schedule_relationship = 0
        # The route_id is set to the GTFS identifier by adding the prefix
        # 'TUS-' ('ayto:linea')
        fe.vehicle.trip.route_id = 'TUS-' + str(item[4])

        # Moment at which the position of the bus was measured. In UNIX time.
        fe.vehicle.timestamp = int(time.mktime(timez.timetuple()))
        # Internal identification of the system for the bus ('ayto: vehiculo').
        fe.vehicle.vehicle.id = str(item[2])
        # Visible label for the user which must be shown to the passenger 
        # to help him identify the bus ('ayto: coche').
        fe.vehicle.vehicle.label = str(item[5])
        # Latitude (EPSG:4326)
        # ('wgs84_pos:lat').
        fe.vehicle.position.latitude = float(item[6])
        # Longitude (EPSG: 4326)
        # ('wgs84_pos:long').
        fe.vehicle.position.longitude = float(item[7])
        # Bus speed in m/s ('ayto:velocidad').
        fe.vehicle.position.speed = float(item[8]) * 1000 / 3600
        # Level of traffic congestion.
        fe.vehicle.congestion_level = 0
        # The vehicle has departed and is in transit to the next stop
        fe.vehicle.current_status = 2

    return fm


# Feed Trip Updates
def buildTripUpdate():
    u"""Build the GTFS Real-Time feed for travel updates (trip update)"""

    con = sqlite3.connect(DIR_TMP + 'bustus.sqlite')
    cursor = con.cursor()
    sql = """SELECT "trip_id",
        "ayto:fechActual",
        "ayto:etiqLinea",
        "dc:identifier",
        "ayto:destino1",
        "ayto:tiempo1",
        "ayto:paradaId"
        FROM control_flotas_estimaciones"""
    cursor.execute(sql)
    estimaciones = cursor.fetchall()
    fm = buildHeader()
    for item in estimaciones:
        timez = dateutil.parser.parse(item[1])  # Hora UTC
        fe = fm.entity.add()

        fe.id = 'trip_update_' + str(item[2]) + '_' + str(item[3])
        tbus = dateutil.parser.parse(item[1])

        t1 = dateutil.parser.parse("00:00:00")
        t2 = dateutil.parser.parse("05:59:59")
        utc = pytz.UTC
        t1 = utc.localize(t1)
        t2 = utc.localize(t2)

        if tbus >= t1 and tbus <= t2:  # Night buses departing the day before.
            tbus = tbus - datetime.timedelta(days=1)
            fe.trip_update.trip.start_date = str(tbus)
        else:
            fe.trip_update.trip.start_date = str(
                tbus.date())  # Date of departure of the trip

        # Lines 17 and 18 have different routes and 'id_route' according to schedule, 
        # but this is not included in the Open Data Santander feed, 
        # so we must determine it through the content of the item 'ayto: destino1'
        if str(item[2]) == '17' and destination.find('bº la torre') == -1:
            fe.trip_update.trip.route_id = 'TUS-' + str(item[2]) + '-1'
        elif str(item[2]) == '17' and destination.find('bº la torre') != -1:
            fe.trip_update.trip.route_id = 'TUS-' + str(item[2]) + '-2'
        elif str(item[2]) == '18' and destination.find('por corbanera') != -1:
            fe.trip_update.trip.route_id = 'TUS-' + str(item[2]) + '-1'
        elif str(item[2]) == '18' and destination.find('por corbanera') == -1:
            fe.trip_update.trip.route_id = 'TUS-' + str(item[2]) + '-2'
        else:
            fe.trip_update.trip.route_id = 'TUS-' + str(item[2])

        stu = fe.trip_update.stop_time_update.add()
        # ETA in UNIX time
        stu.arrival.time = int(time.mktime(timez.timetuple())) + int(item[5])
        stu.stop_id = str(item[6])

        fe.trip_update.vehicle.label = str(item[2])

    return fm


@app.route('/')
def home():
    html = '<p style="text-align: right;"><small>' + \
        str(datetime.datetime.now()) + '</small></p>'
    html = html + """<h1>RISUM Project</h1>
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
            </ul>"""

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


if __name__ == "__main__":
    #host = os.environ['OPENSHIFT_PYTHON_IP']
    #port = int(os.environ['OPENSHIFT_PYTHON_PORT'])

    if 'OPENSHIFT_PYTHON_IP' in os.environ:
        from wsgiref.simple_server import make_server
        httpd = make_server('OPENSHIFT_PYTHON_IP', 8051, app)
        #httpd = make_server(host, port, app)
        # Wait for a single request, serve it and quit.
        # httpd.handle_request()
        # Respond to requests until process is killed
        httpd.serve_forever()
    else:
        app.run(debug=True)

DROP TABLE IF EXISTS agency;
DROP TABLE IF EXISTS calendar;
DROP TABLE IF EXISTS calendar_dates;
DROP TABLE IF EXISTS fare_attributes;
DROP TABLE IF EXISTS fare_rules;
DROP TABLE IF EXISTS frequencies;
DROP TABLE IF EXISTS routes;
--DROP TABLE IF EXISTS shapes;
DROP TABLE IF EXISTS stops;
DROP TABLE IF EXISTS stop_times;
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS tiempos_paradas;

CREATE TABLE agency(agency_id TEXT,
agency_name TEXT,
agency_url TEXT,
agency_timezone TEXT,
agency_phone TEXT,
agency_lang TEXT,
agency_fare_url TEXT);
CREATE TABLE calendar (service_id TEXT,
monday INTEGER,
tuesday INTEGER,
wednesday INTEGER,
thursday INTEGER,
friday INTEGER,
saturday INTEGER,
sunday INTEGER,
start_date INTEGER,
end_date INTEGER);
CREATE TABLE calendar_dates(service_id TEXT,
date INTEGER,
exception_type INTEGER);
CREATE TABLE fare_attributes(fare_id TEXT,
price DOUBLE,
currency_type TEXT,
payment_method INTEGER,
transfers INTEGER,
transfer_duration INTEGER);
CREATE TABLE fare_rules (fare_id TEXT,
route_id TEXT,
origin_id TEXT,
destination_id TEXT,
contains_id TEXT);
CREATE TABLE frequencies (trip_id TEXT,
start_time TEXT,
end_time TEXT,
headway_secs TEXT,
exact_times INTEGER);
CREATE TABLE routes(route_id TEXT,
agency_id TEXT,
route_short_name TEXT,
route_long_name TEXT,
route_desc TEXT,
route_type INTEGER,
route_url TEXT,
route_color TEXT,
route_text_color TEXT);
--CREATE TABLE shapes(shape_id INTEGER,shape_pt_lat DOUBLE,shape_pt_lon DOUBLE,shape_pt_sequence INTEGER,shape_dist_traveled INTEGER);
CREATE TABLE stops(stop_id TEXT,
stop_code INTEGER,
stop_name TEXT,
stop_desc TEXT,
stop_lat DOUBLE,
stop_lon DOUBLE,
zone_id TEXT,
stop_url TEXT,
location_type INTEGER,
parent_station TEXT,
wheelchair_boarding INTEGER);
CREATE TABLE stop_times(trip_id TEXT,
arrival_time TEXT,
departure_time TEXT,
stop_id TEXT,
stop_sequence INTEGER,
stop_headsign TEXT,
pickup_type TEXT,
drop_off_time TEXT,
shape_dist_traveled TEXT,
id_tiempos TEXT);
CREATE TABLE trips(route_id TEXT,
service_id TEXT,
trip_id TEXT,
trip_headsign TEXT,
direction_id INTEGER,
block_id TEXT,
shape_id TEXT,
wheelchair_accessible INTEGER,
horario TEXT);

CREATE TABLE tiempos_paradas(LINEA TEXT,
SECUENCIA INTEGER,
PARADA TEXT,
NOMBRE TEXT,
TIEMPO TEXT,
ORIGEN TEXT,
DESTINO TEXT,
TORIGINAL TEXT,
CALCULO TEXT,
ID_TIEMPOS TEXT);

--TODO: Poner esto despues de la importacion de hojas
DELETE FROM agency WHERE agency_id LIKE 'agency_id';
DELETE FROM calendar WHERE service_id LIKE 'service_id';
DELETE FROM calendar_dates WHERE service_id LIKE 'service_id';
DELETE FROM fare_attributes WHERE fare_id LIKE 'fare_id';
DELETE FROM fare_rules WHERE fare_id LIKE 'fare_id';
DELETE FROM frequencies WHERE trip_id LIKE 'trip_id';
DELETE FROM routes WHERE route_id LIKE 'route_id';
--DELETE FROM shapes WHERE shape_id LIKE 'shape_id';
DELETE FROM stops WHERE stop_id LIKE 'stop_id';
DELETE FROM stop_times WHERE trip_id LIKE 'trip_id';
DELETE FROM trips WHERE route_id LIKE 'route_id';

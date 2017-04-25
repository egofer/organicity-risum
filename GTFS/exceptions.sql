--La linea ALSA-S8 a partir de las 22:20 en Sabados, 22:15 de L-V y 22:45 D-F direccion Liencres -> Santander finaliza en Cuatro Caminos
DELETE FROM stop_times WHERE trip_id = "ALSA-S8A-S-LIE2220DER" AND stop_sequence > 27;
DELETE FROM stop_times WHERE trip_id = "ALSA-S8A-LV-LIE2215DER" AND stop_sequence > 27;
DELETE FROM stop_times WHERE trip_id = "ALSA-S8A-F-LIE2245DER" AND stop_sequence > 27;

--La Linea ALSA-S9 a partir de las 22:10 de L-V y de las 22:40 de D-F direccion Liencres -> Santander finaliza en Cuatro Caminos
DELETE FROM stop_times WHERE trip_id = "ALSA-S9A-LV-MOM2210DER" AND stop_sequence > 31;
DELETE FROM stop_times WHERE trip_id = "ALSA-S9A-F-MOM2240DER" AND stop_sequence > 31;

--La linea RENFE-C1 Reinosa-Santander de las 22:34 no para entre Parbayon y Boo inclusive

DELETE FROM stop_times WHERE (trip_id = "RENFE-C1FE-LV-REI2038DER" AND stop_sequence BETWEEN 2 AND 4) OR (trip_id ="RENFE-C1FE-D-REI2234DER" AND stop_sequence BETWEEN 2 AND 4);
UPDATE stop_times SET stop_sequence = 2 WHERE (trip_id = "RENFE-C1FE-LV-REI2234DER" AND stop_sequence = 5) OR (trip_id ="RENFE-C1FE-D-REI2234DER" AND stop_sequence = 5);
UPDATE stop_times SET stop_sequence = 3 WHERE (trip_id = "RENFE-C1FE-LV-REI2234DER" AND stop_sequence = 6) OR (trip_id ="RENFE-C1FE-D-REI2234DER" AND stop_sequence = 6);
UPDATE stop_times SET stop_sequence = 4 WHERE (trip_id = "RENFE-C1FE-LV-REI2234DER" AND stop_sequence = 7) OR (trip_id ="RENFE-C1FE-D-REI2234DER" AND stop_sequence = 7);
UPDATE stop_times SET stop_sequence = 5 WHERE (trip_id = "RENFE-C1FE-LV-REI2234DER" AND stop_sequence = 8) OR (trip_id ="RENFE-C1FE-D-REI2234DER" AND stop_sequence = 8);
UPDATE stop_times SET stop_sequence = 6 WHERE (trip_id = "RENFE-C1FE-LV-REI2234DER" AND stop_sequence = 9) OR (trip_id ="RENFE-C1FE-D-REI2234DER" AND stop_sequence = 9);

--La linea FEVE-S1 Santander-Oviedo se elimina porque no para entre Santander y Mogro

DELETE FROM trips WHERE trip_id LIKE "FEVE-S1%SAN%EDO";
DELETE FROM stop_times WHERE trip_id LIKE "FEVE-S1%SAN%EDO";
DELETE FROM trips WHERE trip_id LIKE "FEVE-S1%OVI%DER";
DELETE FROM stop_times WHERE trip_id LIKE "FEVE-S1%OVI%DER";

--Las línea FEVE-S1 Santander-Cabezon de la Sal tiene secuencias de paradas distintas en función del horario

---Santander, Valdecilla, Bezana, Torrelavega*, Puente San Miguel*
DELETE FROM stop_times WHERE 
trip_id ="FEVE-S1E-LV-SAN0635UEL" AND stop_sequence IN (3,4,6,7,8) OR 
trip_id ="FEVE-S1E-LV-SAN0805UEL" AND stop_sequence IN (3,4,6,7,8) OR 
trip_id ="FEVE-S1E-LV-SAN1100UEL" AND stop_sequence IN (3,4,6,7,8) OR 
trip_id ="FEVE-S1E-LV-SAN1545UEL" AND stop_sequence IN (3,4,6,7,8) OR 
trip_id ="FEVE-S1E-LV-SAN1700UEL" AND stop_sequence IN (3,4,6,7,8) OR 
trip_id ="FEVE-S1E-LV-SAN1800UEL" AND stop_sequence IN (3,4,6,7,8) OR 
trip_id ="FEVE-S1E-LV-SAN1935EGA" AND stop_sequence IN (3,4,6,7,8) OR 
trip_id ="FEVE-S1E-LV-SAN0940EGA" AND stop_sequence IN (3,4,6,7,8) OR 
trip_id ="FEVE-S1E-LV-SAN0845EGA" AND stop_sequence IN (3,4,6,7,8);

UPDATE stop_times SET stop_sequence = 3 WHERE trip_id IN ("FEVE-S1E-LV-SAN0635UEL", "FEVE-S1E-LV-SAN0805UEL", "FEVE-S1E-LV-SAN1100UEL", "FEVE-S1E-LV-SAN1545UEL", "FEVE-S1E-LV-SAN1700UEL", "FEVE-S1E-LV-SAN1800UEL", "FEVE-S1E-LV-SAN1935EGA", "FEVE-S1E-LV-SAN0940EGA", "FEVE-S1E-LV-SAN0845EGA") AND stop_sequence IN (5);
UPDATE stop_times SET stop_sequence = 4 WHERE trip_id IN ("FEVE-S1E-LV-SAN0635UEL", "FEVE-S1E-LV-SAN0805UEL", "FEVE-S1E-LV-SAN1100UEL", "FEVE-S1E-LV-SAN1545UEL", "FEVE-S1E-LV-SAN1700UEL", "FEVE-S1E-LV-SAN1800UEL", "FEVE-S1E-LV-SAN1935EGA", "FEVE-S1E-LV-SAN0940EGA", "FEVE-S1E-LV-SAN0845EGA") AND stop_sequence IN (6);
UPDATE stop_times SET stop_sequence = 5 WHERE trip_id IN ("FEVE-S1E-LV-SAN0635UEL", "FEVE-S1E-LV-SAN0805UEL", "FEVE-S1E-LV-SAN1100UEL", "FEVE-S1E-LV-SAN1545UEL", "FEVE-S1E-LV-SAN1700UEL", "FEVE-S1E-LV-SAN1800UEL", "FEVE-S1E-LV-SAN1935EGA", "FEVE-S1E-LV-SAN0940EGA", "FEVE-S1E-LV-SAN0845EGA") AND stop_sequence IN (7);
UPDATE stop_times SET stop_sequence = 6 WHERE trip_id IN ("FEVE-S1E-LV-SAN0635UEL", "FEVE-S1E-LV-SAN0805UEL", "FEVE-S1E-LV-SAN1100UEL", "FEVE-S1E-LV-SAN1545UEL", "FEVE-S1E-LV-SAN1700UEL", "FEVE-S1E-LV-SAN1800UEL", "FEVE-S1E-LV-SAN1935EGA", "FEVE-S1E-LV-SAN0940EGA", "FEVE-S1E-LV-SAN0845EGA") AND stop_sequence IN (8);

---Santander, Valdecilla, Bezana. Mortera, Boo de Piélagos, Mogro, Barreda*, Torrelavega*, Puente San Miguel*
DELETE FROM stop_times WHERE trip_id ="FEVE-S1E-LV-SAN0725UEL" AND stop_sequence IN (3,4);
UPDATE stop_times SET stop_sequence = 3 WHERE (trip_id = "FEVE-S1E-LV-SAN0725UEL" AND stop_sequence = 5);
UPDATE stop_times SET stop_sequence = 4 WHERE (trip_id = "FEVE-S1E-LV-SAN0725UEL" AND stop_sequence = 6);
UPDATE stop_times SET stop_sequence = 5 WHERE (trip_id = "FEVE-S1E-LV-SAN0725UEL" AND stop_sequence = 7);
UPDATE stop_times SET stop_sequence = 6 WHERE (trip_id = "FEVE-S1E-LV-SAN0725UEL" AND stop_sequence = 8);

---Torrelavega*, Bezana, Valdecilla Santander

DELETE FROM stop_times WHERE trip_id IN ("FEVE-S1E-LV-PUE0726DER", "FEVE-S1E-LV-PUE0857DER", "FEVE-S1E-LV-TOR0920DER", "FEVE-S1E-LV-TOR1020DER", "FEVE-S1E-LV-PUE1149DER", "FEVE-S1E-LV-TOR1429DER", "FEVE-S1E-LV-PUE1634DER", "FEVE-S1E-LV-PUE1737DER", "FEVE-S1E-LV-PUE1837DER", "FEVE-S1E-LV-TOR2025DER", "FEVE-S1E-LV-TOR2125DER", "FEVE-S1E-LV-CAB2304DER", "FEVE-S1E-SD-CAB2304DER") AND stop_sequence IN (2,3,6);

/*
DELETE FROM stop_times WHERE 
trip_id ="FEVE-S1E-LV-PUE0726DER" AND stop_sequence IN (1,2,3,6) OR 
trip_id ="FEVE-S1E-LV-PUE0857DER" AND stop_sequence IN (1,2,3,6) OR 
trip_id ="FEVE-S1E-LV-TOR0920DER" AND stop_sequence IN (1,2,3,6) OR 
trip_id ="FEVE-S1E-LV-TOR1020DER" AND stop_sequence IN (1,2,3,6) OR 
trip_id ="FEVE-S1E-LV-PUE1149DER" AND stop_sequence IN (1,2,3,6) OR 
trip_id ="FEVE-S1E-LV-TOR1429DER" AND stop_sequence IN (1,2,3,6) OR 
trip_id ="FEVE-S1E-LV-PUE1634DER" AND stop_sequence IN (1,2,3,6) OR 
trip_id ="FEVE-S1E-LV-PUE1737DER" AND stop_sequence IN (1,2,3,6) OR 
trip_id ="FEVE-S1E-LV-PUE1837DER" AND stop_sequence IN (1,2,3,6) OR 
trip_id ="FEVE-S1E-LV-TOR2025DER" AND stop_sequence IN (1,2,3,6) OR 
trip_id ="FEVE-S1E-LV-TOR2125DER" AND stop_sequence IN (1,2,3,6) OR 
trip_id ="FEVE-S1E-LV-CAB2304DER" AND stop_sequence IN (1,2,3,6) OR 
trip_id ="FEVE-S1E-SD-CAB2304DER" AND stop_sequence IN (1,2,3,6);
*/

UPDATE stop_times SET stop_sequence = 2 WHERE trip_id IN ("FEVE-S1E-LV-PUE0726DER", "FEVE-S1E-LV-PUE0857DER", "FEVE-S1E-LV-TOR0920DER", "FEVE-S1E-LV-TOR1020DER", "FEVE-S1E-LV-PUE1149DER", "FEVE-S1E-LV-TOR1429DER", "FEVE-S1E-LV-PUE1634DER", "FEVE-S1E-LV-PUE1737DER", "FEVE-S1E-LV-PUE1837DER", "FEVE-S1E-LV-TOR2025DER", "FEVE-S1E-LV-TOR2125DER", "FEVE-S1E-LV-CAB2304DER", "FEVE-S1E-SD-CAB2304DER") AND stop_sequence = 7;
UPDATE stop_times SET stop_sequence = 3 WHERE trip_id IN ("FEVE-S1E-LV-PUE0726DER", "FEVE-S1E-LV-PUE0857DER", "FEVE-S1E-LV-TOR0920DER", "FEVE-S1E-LV-TOR1020DER", "FEVE-S1E-LV-PUE1149DER", "FEVE-S1E-LV-TOR1429DER", "FEVE-S1E-LV-PUE1634DER", "FEVE-S1E-LV-PUE1737DER", "FEVE-S1E-LV-PUE1837DER", "FEVE-S1E-LV-TOR2025DER", "FEVE-S1E-LV-TOR2125DER", "FEVE-S1E-LV-CAB2304DER", "FEVE-S1E-SD-CAB2304DER") AND stop_sequence = 8;

--La Linea ALSA-S5 a las 7:00 de L-V dirección Santander-Maono vuelve por Muriedas-Revilla-Escobedo (comparte con linea ALSA-S6)
DELETE FROM stop_times WHERE trip_id = "ALSA-S5-LV-MAO0700DER";
DELETE FROM stop_times WHERE trip_id = "ALSA-S6-LV-SAN0725EDO";
DELETE FROM trips WHERE trip_id = "ALSA-S5-LV-MAO0700DER";
DELETE FROM trips WHERE trip_id = "ALSA-S6-LV-SAN0725EDO";

--La Linea ALSA-S5 a las 21:25 de L-V dirección Santander-Maono vuelve por Muriedas-Revilla-Escobedo (comparte con linea ALSA-S6)
DELETE FROM stop_times WHERE trip_id = "ALSA-S5-LV-MAO2125DER";
DELETE FROM stop_times WHERE trip_id = "ALSA-S6-LV-SAN2100EDO";
DELETE FROM trips WHERE trip_id = "ALSA-S5-LV-MAO2125DER";
DELETE FROM trips WHERE trip_id = "ALSA-S6-LV-SAN2100EDO";

--La Linea ALSA-S5 a las 7:00 de Sabados dirección Santander-Maono vuelve por Muriedas-Revilla-Escobedo (comparte con linea ALSA-S6)
DELETE FROM stop_times WHERE trip_id = "ALSA-S5A-S-MAO0700DER";
DELETE FROM stop_times WHERE trip_id = "ALSA-S6A-S-SAN0725EDO";
DELETE FROM trips WHERE trip_id = "ALSA-S5A-S-MAO0700DER";
DELETE FROM trips WHERE trip_id = "ALSA-S6A-S-SAN0725EDO";

--La Linea ALSA-S5 a las 21:25 de Sabado dirección Santander-Maono vuelve por Muriedas-Revilla-Escobedo (comparte con linea ALSA-S6)
DELETE FROM stop_times WHERE trip_id = "ALSA-S5A-S-MAO0700DER";
DELETE FROM stop_times WHERE trip_id = "ALSA-S6A-S-SAN0725EDO";
DELETE FROM trips WHERE trip_id = "ALSA-S5A-S-MAO0700DER";
DELETE FROM trips WHERE trip_id = "ALSA-S6A-S-SAN0725EDO";

--La Linea ALSA-S5 a las 13:00 de Sabado dirección Santander-Maono vuelve por Muriedas-Revilla-Escobedo (comparte con linea ALSA-S6)
DELETE FROM stop_times WHERE trip_id = "ALSA-S5A-S-MAO1325DER";
DELETE FROM stop_times WHERE trip_id = "ALSA-S6A-S-SAN1300EDO";
DELETE FROM trips WHERE trip_id = "ALSA-S5A-S-MAO1325DER";
DELETE FROM trips WHERE trip_id = "ALSA-S6A-S-SAN1300EDO";

--Linea S10 indicar horas en que solo operan en periodo no lectivo (vaciones escolares)

UPDATE trips SET trip_headsign = "Oruña → Santander (solo en periodo no lectivo)" WHERE trip_id = "ALSA-S10A-LV-ORU0920DER";
UPDATE trips SET trip_headsign = "Oruña → Santander (solo en periodo no lectivo)" WHERE trip_id = "ALSA-S10A-LV-ORU1630DER";

--Linea S10 indicar horas en que solo operan en periodo lectivo
UPDATE trips SET trip_headsign = "Oruña → Santander (solo en periodo lectivo)" WHERE trip_id = "ALSA-S10A-LV-ORU0900DER";
UPDATE trips SET trip_headsign = "Oruña → Santander (solo en periodo lectivo)" WHERE trip_id = "ALSA-S10A-LV-ORU0930DER";
UPDATE trips SET trip_headsign = "Oruña → Santander (solo en periodo lectivo)" WHERE trip_id = "ALSA-S10A-LV-ORU1700DER";
UPDATE trips SET trip_headsign = "Oruña → Santander (solo en periodo lectivo)" WHERE trip_id = "ALSA-S10A-LV-ORU1745DER";

UPDATE trips SET trip_headsign = "Santander → Oruña (solo en periodo lectivo)" WHERE trip_id = "ALSA-S10A-LV-SAN1000UNA";
UPDATE trips SET trip_headsign = "Santander → Oruña (solo en periodo lectivo)" WHERE trip_id = "ALSA-S10A-LV-SAN1830UNA";





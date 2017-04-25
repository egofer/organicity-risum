DROP TABLE IF EXISTS control_flotas_posiciones;
DROP TABLE IF EXISTS control_flotas_estimaciones;
DROP TABLE IF EXISTS programacionTUS_horariosLineas;
DROP TABLE IF EXISTS programaTUS_horariosTarjetas;
DROP TABLE IF EXISTS calendario_laboral;
DROP TABLE IF EXISTS posicion_vehiculos;

CREATE TABLE "control_flotas_posiciones" (
"ayto:vehiculo" INTEGER,
"ayto:indice" INTEGER,
"ayto:linea" INTEGER,
"ayto:coche" INTEGER,
"ayto:servicio" TEXT,
"gn:coordX" DOUBLE,
"gn:coordY" DOUBLE,
"wgs84_pos:lat" DOUBLE,
"wgs84_pos:long" DOUBLE,
"ayto:estado" INTEGER,
"ayto:instante" TEXT,
"ayto:velocidad" DOUBLE,
"dc:modified" TEXT,
"uri" TEXT);

CREATE TABLE "control_flotas_estimaciones" (
"dc:identifier" INTEGER,
"ayto:etiqLinea" TEXT,
"ayto:fechActual" TEXT,
"ayto:tiempo1" INTEGER,
"ayto:distancia1" INTEGER,
"ayto:paradaId" INTEGER,
"ayto:destino1" TEXT,
"ayto:tiempo2" INTEGER,
"ayto:distancia2" INTEGER,
"ayto:destino2" TEXT,
"dc:modified" TEXT,
"uri" TEXT);

CREATE TABLE "programacionTUS_horariosLineas" (
"dc:identifier" TEXT,
"dc:modified" TEXT,
"ayto:tipoDia" TEXT,
"ayto:linea" INTEGER,
"ayto:servicio" INTEGER,
"ayto:numViaje" INTEGER,
"ayto:tipoParada" INTEGER,
"ayto:idParada" INTEGER,
"ayto:nombreParada" TEXT,
"ayto:idEvento" INTEGER,
"ayto:descEvento" TEXT,
"ayto:hora" INTEGER,
"uri" TEXT
);

CREATE TABLE "programaTUS_horariosTarjetas" (
"dc:identifier" TEXT,
"dc:modified" TEXT,
"ayto:tarjeta" TEXT,
"ayto:dia" TEXT,
"uri" TEXT);

CREATE TABLE "calendario_laboral" (
"dc:identifier" TEXT,
"dc:modified" TEXT,
"ayto:dia" TEXT,
"dc:description" TEXT,
"ayto:tipo" TEXT,
"uri" TEXT);

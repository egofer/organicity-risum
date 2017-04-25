A static GTFS generator for Urban Transport of Santander (TUS) agency. Create a structure of a GTFS Feed with a series of CSV file with information about trips, schedules and associated geographic information.

Install
---------

pip install -r requirements.txt

download.py Download the necessary data from the open data portal of the city of Santander and process them.

server.py Provides two types of data using GTFS-realtime feed: vehicle positions and trip updates.


TUS GTFS-realtime Generator
===========================

This program retrieves real-time transit data from [Transportes Urbanos de Santander](http://www.tusantander.es) (TUS)'s Exploitation Aid System (EAS) and produces Trip Updates and Vehicle Positions files in GTFS-realtime format.

This software is part of the [RISUM project](https://risum.altergeosistemas.com), which is an experiment developed within the European Union's [Organicity project](http://organicity.eu/).

This project has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 645198.

Deployment of this application
------------------------------

- Create a Python application on an OpenShift instance:

```bash
rhc app create gtfs python-2.7
```

- Access to  ./app-root/repo using SSH:

```bash
ssh xxxxxxxxxxxxxxxxxxxxxxxx@gtfs-altergeo.rhcloud.com
cd app-root/repo
```

- Replace requirements.txt with the existing one in the project.

- Copy the files gtfs.py, gtfs-realtime.proto and gtfsrealtimepb2.py into the directory.

- Edit wgsi.py and replace the content with:

```python
#!/usr/bin/python
import os
 
virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
#virtenv = os.path.join(os.environ.get('OPENSHIFT_PYTHON_DIR','.'), 'virtenv')
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
try:
    execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    pass
 
#
# IMPORTANT: Put any additional includes below this line.  If placed above this
# line, it's possible required libraries won't be in your searchable path
#
 
from gtfs import app as application
 
#
# Below for testing only
#
```

- Instalar los paquetes de Python necesarios:

```bash
pip install -r requirements.txt --no-cache-dir
```

- Run the program:

```bash
python wsgi.py
```

- Browser to http://gtfs-altergeo.rhcloud.com

# Mysportsplanner exporter
prometheus metrics for mysportsplanner.com


### Help

````bash
Help

    Execute:
        exporter.py [--username=<username>]
                    [--password=<password>]
                    [--port=<port>]
                    [--pages=<number of pages>]
                    [--help]
        exporter.py --username=your.name@somedomain.org
                    --password=yoursecretpassword
                    --pages=30
                    --port=5000

    Endpoints:
        # curl http://127.0.0.1:5000/metrics
        # curl http://127.0.0.1:5000/status

    notes:
        Default number of pages is 10
        Default port: 5000
````


### Run exporter once

````bash
# python3 ./exporter.py --username=<USERNAME> --password=<PASSWORD> --pages=6 --port=5000
````

### Build container

````bash
# podman build -t mysportsplanner-exporter -f ./Containerfile
````

### Run container

````bash
# podman run --rm --name mysportsplanner-exporter -p 5000:5000 localhost/mysportsplanner-exporter \
             --username=somename \
             --password=somepassword \
             --pages=10 \
             --port=5000
````

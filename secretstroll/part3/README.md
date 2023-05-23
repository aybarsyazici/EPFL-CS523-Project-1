# Running

## Task 3
### Data Collection
Fire up the docker containers, and boot up the server.
Initialization:


Open a shell
```
$ cd cs523/secretstroll
$ docker compose build
$ docker compose up -d
```

Server side:

Open a shell
```
$ cd cs523/secretstroll
$ docker exec -it cs523-server /bin/bash
(server) $ cd /server
(server) $ python3 server.py setup -s key.sec -p key.pub -S restaurant -S bar -S dojo
(server) $ python3 server.py run -D fingerprint.db -s key.sec -p key.pub
```

Client side:
```
Open a shell
$ cd cs523/secretstroll
$ docker exec -it cs523-client /bin/bash
(client) $ cd /client
(client) $ python3 client.py get-pk
(client) $ python3 client.py register -u your_name -S restaurant -S bar -S dojo
(client) $ python3 data_collect.py --min 1 --max 100 --requests 50 -T restaurant
```

This will run the data collection procedure on grids [1, 100] with 50 traces per grid. The client will only query for the restaurants. These are the exact same parameters used in the evaluation part of the report.

WARNING: Takes a lot of time!

### Fingerprinting
Fingerprinting should be run **locally**. First, boot up a virtual environment. Then, install the requirements in `requirements_fingerprinting.tx` before running the script.

```bash
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements_fingerprinting.txt
(venv) $ python fingerprinting.py
```
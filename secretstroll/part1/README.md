# Running
### Client & Server
The docker infrastructure remains the same.
Initialization:
Open a shell
```bash
$ docker compose build
$ docker compose up -d
```
Server side:
Open a shell
```bash
$ docker exec -it cs523-server /bin/bash
(server) $ cd /server
(server) $ python3 server.py setup -s key.sec -p key.pub -S restaurant -S bar -S dojo
(server) $ python3 server.py run -D fingerprint.db -s key.sec -p key.pub
```
Client side:
Open a shell
```bash
$ docker exec -it cs523-client /bin/bash
(client) $ cd /client
(client) $ python3 client.py get-pk
(client) $ python3 client.py register -u your_name -S restaurant -S bar -S dojo
(client) $ python3 client.py loc 46.52345 6.57890 -T restaurant -T bar
```

Close everything down at the end of the experiment:
```
$ docker compose down
```

### Tests
To test the code we have written a test docker container. To run the tests, run:
```bash
# the rm flag removes the container after the tests are run
$ docker-compose -f ./docker-compose.test.yml run --rm testing
# could also use the command below, but this causes the output to be less readable, thus not recommended
$ docker-compose -f ./docker-compose.test.yml up -d 
```
These commands will run all the tests using pytest in test_registrationscheme.py and test_signaturescheme.py

### Measurements
!!!!!TODO!!!!!
Similar to the tests, measurements should be taken from inside one of the Docker containers. To perform measurements, run:

```bash
$ python3 measurements.py measure -o measurements/raw.csv -r 100
```

This will take raw measurements over 100 iterations and save it to `measurements/raw.csv`. To aggregate the results, run:

```bash
$ python3 measurements.py aggregate -i measurements/raw.csv -o measurements/stat.csv
```

This will aggregate the results and output the results to `measurements/stat/csv`.

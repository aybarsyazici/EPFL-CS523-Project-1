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
# below line is not necessary if the client has already received the pk key, i.e. key-client.pub exists.
(client) $ python3 client.py get-pk
# below line is not necessary if the client is already registered, i.e. the anon.cred file exists.
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
$ docker-compose -f ./docker-compose-testing.yaml run --rm testing
# could also use the command below, but this causes the output to be less readable, thus not recommended
$ docker-compose -f ./docker-compose-testing.yaml up -d 
```
These commands will run all the tests using pytest in test_registrationscheme.py and test_signaturescheme.py

### Measurements
Measurements are taken by evaluation.py, which should be run from inside one of the docker containers. To run, start the client's or server's docker container as explained above, and execute the following command inside the container:

```bash
$ python3 evaluation.py 100
```

This will run the evaluation script 100 times and save the results in the measurements folder. In this folder, one can find the measurements of the functions that we included in the report.
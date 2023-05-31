# Running

## Task 3
### Data Collection
Fire up the docker containers, and boot up the server.
Initialization:
Open a shell
```
$ docker compose build
$ docker compose up -d
```
 
Assuming that the server already has the keys generated: If not first generate the keys:
Server side:
```bash
#Open a shell
$ docker exec -it cs523-server /bin/bash
(server) $ cd /server
# below line is not necessary if the keys are already generated 
(server) $ python3 server.py setup -s key.sec -p key.pub -S restaurant -S bar -S dojo 
(server) $ python3 server.py run -D fingerprint.db -s key.sec -p key.pub
```

Assuming the client has already registered: If not first register:
```bash
#Open a shell
$ docker exec -it cs523-client /bin/bash
(client) $ cd /client
# below line is not necessary if the client has already received the pk key, i.e. key-client.pub exists.
(client) $ python3 client.py get-pk
# below line is not necessary if the client is already registered
(client) $ python3 client.py register -u your_name -S restaurant -S bar -S dojo
(client) $ python3 data_collect.py --min 1 --max 100 --requests 50 -T restaurant
```
This will give the results discussed in the report, and will save the data as .pcapng files under the ./data directory.
!!!!!!WARNING: Takes a really long amount of time!!!!!!

To run the the fingerprinting, we need to extract features from these files. This can be done in two ways:

1. import data_sanitize.py and run:
```python
# Get traces
traces = data_sanitize.get_traces()
# Now get the features from the traces, returns numpy array
training_data = data_sanitize.get_training_data_from_traces(traces)
```
2. Or instead you can run it from the command line:
```bash
python3 ./data_sanitizer.py
```
Which will do the steps described above and save the training data as .npy files for each grid under ./data/features_extracted_per_grid. 
You can import these data and convert them to numpy arrays manually or again you can import data_sanitize.py and just run:
```python
# This function looks for data under ./data/features_extracted_per_grid and returns the training data as a numpy array
training_data = data_sanitize.get_saved_training_data()
```

### Fingerprinting
Fingerprinting is done locally, without Docker. First, boot up a virtual environment. Then, install the requirements in `requirements_fingerprinting.txt` before running the script.

```bash
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements_fingerprinting.txt
(venv) $ python3 fingerprinting.py
```
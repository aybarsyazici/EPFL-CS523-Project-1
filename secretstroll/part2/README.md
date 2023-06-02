# Task 2

For this part most of our implementations are explained in the notebook(Don't forget to install the `requirements_privacy_evaluation.txt` file before running the notebook).

To evaluate the defence we have suggested, we have done a small scale data collection. For that we have modified client.py and added a new argument to it called eval
Firstly, setup client and server as explained in the previous sections:
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
# If the server already has keys setup, you can skip the below command
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
# If the client is already registered you can skip the below command...
(client) $ python3 client.py register -u your_name -S restaurant -S bar -S dojo
(client) $ python3 client.py eval 46.52345 6.57890 -T restaurant -T bar -n 1000
```
The command eval gets -n, which is the number of times to run. When executed the command queries the server with the actual position once and also once with the obfuscated location using epsilon = 7.25, as explained in the report. Then it records the returned PoIs for the actual location and obfuscated location. It also calculated the grid of the actual position and the noisy location. Because the server returns the locations based on the grid that the user is currently.

After getting the data, it will be written in runs.npy file. Which we explore in the privacy-evaluation.ipynb notebook.

Don't forget to close everything down at the end of the experiment:
```
$ docker compose down
```


import argparse
from datetime import datetime
import functools
import hashlib
import os
import subprocess as sp
import time

def collect_trace(id, run, grid, subs):
    time_name = datetime.now().strftime("%d-%m-%y %H.%M.%S")
    output_file_name = f"{id} - g{grid}r{run} - {time_name}.pcapng"
    wait_time = 1
    while True:
        # First, start the tcpdump in the background.
        tcpdump_process = sp.Popen(["tcpdump", "-w", f"data/{output_file_name}"])
        # Then, start the client and block.
        subs_cmdlet = functools.reduce(list.__add__, [["-T", sub] for sub in subs])
        client_cmd = ["python3", "client.py", "grid", f"{grid}"] + subs_cmdlet + ["-t"]
        print(" ".join(client_cmd))
        client_result = sp.run(client_cmd, capture_output=True, text=True)
        # print(client_result.stdout)
        # Terminate tcpdump after the client terminates.
        time.sleep(0.5)
        tcpdump_process.terminate()
        if "Traceback" not in client_result.stderr:
            break
        else:
            # print(client_result.stderr)
            print("!!! Error detected. Retrying...")
            wait_time *= 2
            time.sleep(wait_time)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data collection for part 3")
    parser.add_argument("--min", default=1, type=int, help="min grid")
    parser.add_argument("--max", default=100, type=int, help="max grid (inclusive)")
    parser.add_argument("--requests", "-r", required=True, type=int, help="number of requests per grid")
    parser.add_argument("-T", "--types", help="types of services to request", type=str, required=True, action="append")    
    args = parser.parse_args()
    # Create the data directory.
    os.makedirs("data", exist_ok=True)
    # Create a unique id for this data collection session.
    id = hashlib.md5(datetime.now().strftime("%d-%m-%y %H.%M.%S").encode()).hexdigest()[:10]
    # Start collecting the data.
    for grid in range(args.min, args.max+1):
        for i in range(args.requests):
            print(f"\n*** Run {i+1}/{args.requests} for grid {grid}")
            collect_trace(id, i, grid, args.types)
            time.sleep(1)
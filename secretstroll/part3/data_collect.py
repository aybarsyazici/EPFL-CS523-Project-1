import argparse
from datetime import datetime
import functools
import hashlib
import os
import subprocess as sp
import time

def collect_trace(id, run, grid, subs):
    timestamp = datetime.now().strftime("%d-%m-%y %H.%M.%S")
    out_file_name = f"{id} - g{grid}r{run} - {timestamp}.pcapng"
    wait_time = 1
    while True:
        tcpdump_process = sp.Popen(["tcpdump", "-w", f"data/{out_file_name}"])
        subs_cmdlet = functools.reduce(list.__add__, [["-T", sub] for sub in subs])
        client_cmd = ["python3", "client.py", "grid", f"{grid}"] + subs_cmdlet + ["-t"]
        client_result = sp.run(client_cmd, capture_output=True, text=True)
        time.sleep(0.5)
        tcpdump_process.terminate()
        if "Traceback" not in client_result.stderr:
            break
        else:
            wait_time *= 2
            print("Retrying ... ", client_result.stderr)
            time.sleep(wait_time)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect TCPDUMP traces for a grid")
    parser.add_argument("--min", default=1, type=int, help="Starting grid label")
    parser.add_argument("--max", default=100, type=int, help="Ending grid label inclusive")
    parser.add_argument("--runs", "-r", required=True, type=int, help="Number of runs per grid")
    parser.add_argument("-T", "--types", help="Types to request", type=str, required=True, action="append")    
    args = parser.parse_args()
    os.makedirs("data", exist_ok=True)
    # Create a unique id by:
    # 1. Getting the current time.
    # 2. Converting it to a string format(dd-mm-yy HMS).
    # 3. Encoding it to bytes.
    # 4. Hashing it with md5.
    # 5. Getting the first 10 characters.
    id = hashlib.md5(datetime.now().strftime("%d-%m-%y %H.%M.%S").encode()).hexdigest()[:10]
    # Data collection
    for grid in range(args.min, args.max+1):
        for i in range(args.runs):
            print(f"\n*** Run {i+1}/{args.runs} for grid {grid}")
            collect_trace(id, i, grid, args.types)
            time.sleep(1)
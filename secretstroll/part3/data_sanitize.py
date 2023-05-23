# main func
import dpkt
from typing import List, Dict, Tuple, Set
from tqdm import tqdm
from glob import glob
from scapy.all import *
from collections import Counter
import numpy as np
import os

# server ip: '172.21.0.3'
# client ip (normally):  '172.21.0.2'

# logger levels enum
class LogLevel:
    VERBOSE = 0
    GENERAL = 1
    CRITICAL = 2

class Logger:
    logging:LogLevel = LogLevel.GENERAL

    def verbose(self, msg):
        if self.logging == LogLevel.VERBOSE:
            print(msg)
    def general(self, msg):
        if self.logging <= LogLevel.GENERAL:
            print(msg)

logger = Logger()

# Represents a network trace with two participants.
class NetworkTrace:
    def __init__(self, packets, sender, receiver, grid:int):
        self.packets = packets
        self.sender = sender
        self.receiver = receiver
        self.grid = grid
    # str func
    def __str__(self):
        return f"NetworkTrace(sender={self.sender}, receiver={self.receiver}, packets={len(self.packets)})"

class Data:
    def __init__(self, 
                 label:int, 
                 num_outgoing, 
                 num_incoming, 
                 total_packets,
                 outgoing_ratio, 
                 incoming_ratio, 
                 outgoing_bytes, 
                 incoming_bytes,
                 avg_outgoing_bytes,
                 avg_incoming_bytes,
                 std_outgoing_bytes,
                 std_incoming_bytes,
                 min_outgoing_bytes,
                 min_incoming_bytes,
                 max_outgoing_bytes,
                 max_incoming_bytes,  
                 avg_outgoing_freq, 
                 avg_incoming_freq,
                 std_outgoing_freq,
                 std_incoming_freq,
                 min_outgoing_freq,
                 min_incoming_freq,
                 max_outgoing_freq,
                 max_incoming_freq,
                 avg_outgoing_ordering,
                 std_outgoing_ordering,
                 ):
        self.label = label
        self.num_outgoing = num_outgoing
        self.num_incoming = num_incoming
        self.total_packets = total_packets
        self.outgoing_ratio = outgoing_ratio
        self.incoming_ratio = incoming_ratio
        self.outgoing_bytes = outgoing_bytes
        self.incoming_bytes = incoming_bytes
        self.avg_outgoing_freq = avg_outgoing_freq
        self.avg_incoming_freq = avg_incoming_freq
        self.std_outgoing_freq = std_outgoing_freq
        self.std_incoming_freq = std_incoming_freq
        self.avg_outgoing_bytes = avg_outgoing_bytes
        self.avg_incoming_bytes = avg_incoming_bytes
        self.std_outgoing_bytes = std_outgoing_bytes
        self.std_incoming_bytes = std_incoming_bytes
        self.min_outgoing_bytes = min_outgoing_bytes
        self.min_incoming_bytes = min_incoming_bytes
        self.max_outgoing_bytes = max_outgoing_bytes
        self.max_incoming_bytes = max_incoming_bytes
        self.min_outgoing_freq = min_outgoing_freq
        self.min_incoming_freq = min_incoming_freq
        self.max_outgoing_freq = max_outgoing_freq
        self.max_incoming_freq = max_incoming_freq
        self.avg_outgoing_ordering = avg_outgoing_ordering
        self.std_outgoing_ordering = std_outgoing_ordering

    def to_numpy(self):
        return np.array([
            self.label,
            self.num_outgoing,
            self.num_incoming,
            self.total_packets,
            self.outgoing_ratio,
            self.incoming_ratio,
            self.outgoing_bytes,
            self.incoming_bytes,
            self.avg_outgoing_freq,
            self.avg_incoming_freq,
            self.std_outgoing_freq,
            self.std_incoming_freq,
            self.avg_outgoing_bytes,
            self.avg_incoming_bytes,
            self.std_outgoing_bytes,
            self.std_incoming_bytes,
            self.min_outgoing_bytes,
            self.min_incoming_bytes,
            self.max_outgoing_bytes,
            self.max_incoming_bytes,
            self.min_outgoing_freq,
            self.min_incoming_freq,
            self.max_outgoing_freq,
            self.max_incoming_freq,
            self.avg_outgoing_ordering,
            self.std_outgoing_ordering,
        ])

def get_traces() -> List[NetworkTrace]:
    traces = {}
    for filename in tqdm(glob('./data/*'), desc="Reading traces..."):
        # if filename is a directory, skip it
        if os.path.isdir(filename):
            continue
        # if filename does not end with .pcap, skip it
        if not filename.endswith('.pcapng'):
            continue
        with open(filename, 'rb') as fp:
            # get the substring from file name that is between the first '-' and second '-'
            # this is the grid name and round number
            grid_name = filename[filename.find('-')+3:filename.find('-', filename.find('-')+1)]
            # remove round number from grid name, i.e take the substring from the start till the 'r' character
            grid_count = int(grid_name[0:grid_name.find('r')])
            if grid_count not in traces:
                traces[grid_count] = []
            pcap = dpkt.pcap.Reader(fp)
            all_senders = []
            all_receivers = []
            packets = []
            for ts, buf in pcap:
                eth = dpkt.ethernet.Ethernet(buf)
                if eth.type!=dpkt.ethernet.ETH_TYPE_IP:
                    continue
                # get the sender and receiver ip addresses
                ip = eth.data
                src = socket.inet_ntoa(ip.src)
                dst = socket.inet_ntoa(ip.dst)
                all_senders.append(src)
                all_receivers.append(dst)
                logger.verbose(f"All senders: {all_senders} | All receivers: {all_receivers}")
                packets.append((ts,ip))
            traces[grid_count].append(
                NetworkTrace(
                packets, 
                Counter(all_senders).most_common(1)[0][0], 
                Counter(all_receivers).most_common(1)[0][0],
                grid_count
                )
            )
    return traces

def feature_extraction(trace: NetworkTrace):
    logger.verbose(f"Sender: {trace.sender}")
    logger.verbose(f"Receiver: {trace.receiver}")
    # get the number of outgoing packets
    outgoing_packets = len([pkt for ts, pkt in trace.packets if socket.inet_ntoa(pkt.src) == trace.sender])
    # get the number of incoming packets
    incoming_packets = len([pkt for ts, pkt in trace.packets if socket.inet_ntoa(pkt.src) == trace.receiver])
    logger.verbose(f"Outgoing packets: {outgoing_packets}")
    logger.verbose(f"Incoming packets: {incoming_packets}")
    total_packets = len(trace.packets)
    # Get the ratio of outgoing and incoming packets
    outgoing_ratio = outgoing_packets / (total_packets)
    incoming_ratio = incoming_packets / (total_packets)
    logger.verbose(f"Outgoing ratio: {outgoing_ratio}")
    logger.verbose(f"Incoming ratio: {incoming_ratio}")
    # Get the outgoing byte size
    outgoing_bytes = sum([len(pkt) for ts, pkt in trace.packets if socket.inet_ntoa(pkt.src) == trace.sender])
    incoming_bytes = sum([len(pkt) for ts, pkt in trace.packets if socket.inet_ntoa(pkt.src) == trace.receiver])
    # get the avg 
    avg_outgoing_byte = np.mean([len(pkt) for ts, pkt in trace.packets if socket.inet_ntoa(pkt.src) == trace.sender])
    avg_incoming_byte = np.mean([len(pkt) for ts, pkt in trace.packets if socket.inet_ntoa(pkt.src) == trace.receiver])
    # get the std of outgoing bytes
    std_outgoing_byte = np.std([len(pkt) for ts, pkt in trace.packets if socket.inet_ntoa(pkt.src) == trace.sender])
    std_incoming_byte = np.std([len(pkt) for ts, pkt in trace.packets if socket.inet_ntoa(pkt.src) == trace.receiver])
    # get the max outgoing bytesize
    max_outgoing_byte = np.max([len(pkt) for ts, pkt in trace.packets if socket.inet_ntoa(pkt.src) == trace.sender])
    max_incoming_byte = np.max([len(pkt) for ts, pkt in trace.packets if socket.inet_ntoa(pkt.src) == trace.receiver])
    # get the min outgoing bytesize
    min_outgoing_byte = np.min([len(pkt) for ts, pkt in trace.packets if socket.inet_ntoa(pkt.src) == trace.sender])
    min_incoming_byte = np.min([len(pkt) for ts, pkt in trace.packets if socket.inet_ntoa(pkt.src) == trace.receiver])
    logger.verbose(f"Outgoing bytes: {outgoing_bytes}")
    logger.verbose(f"Incoming bytes: {incoming_bytes}")
    logger.verbose(f"Total bytes: {sum([len(pkt) for ts, pkt in trace.packets])} | {outgoing_bytes + incoming_bytes}")
    # get the avreage time between outgoing packets
    outging_timestamps = [ts for ts,pkt in trace.packets if socket.inet_ntoa(pkt.src) == trace.sender]
    incoming_timestamps = [ts for ts,pkt in trace.packets if socket.inet_ntoa(pkt.src) == trace.receiver]
    # sort the two arrays by timestamp
    outging_timestamps.sort()
    incoming_timestamps.sort()
    average_outgoing_freq = np.mean([outging_timestamps[i+1] - outging_timestamps[i] for i in range(len(outging_timestamps)-1)])
    average_incoming_freq = np.mean([incoming_timestamps[i+1] - incoming_timestamps[i] for i in range(len(incoming_timestamps)-1)])
    # get the std of the time between outgoing packets
    std_outgoing_freq = np.std([outging_timestamps[i+1] - outging_timestamps[i] for i in range(len(outging_timestamps)-1)])
    std_incoming_freq = np.std([incoming_timestamps[i+1] - incoming_timestamps[i] for i in range(len(incoming_timestamps)-1)])
    # max time between outgoing packets
    max_outgoing_freq = np.max([outging_timestamps[i+1] - outging_timestamps[i] for i in range(len(outging_timestamps)-1)])
    max_incoming_freq = np.max([incoming_timestamps[i+1] - incoming_timestamps[i] for i in range(len(incoming_timestamps)-1)])
    # min time between outgoing packets
    min_outgoing_freq = np.min([outging_timestamps[i+1] - outging_timestamps[i] for i in range(len(outging_timestamps)-1)])
    min_incoming_freq = np.min([incoming_timestamps[i+1] - incoming_timestamps[i] for i in range(len(incoming_timestamps)-1)])
    # ordering
    avg_outgoing_ordering = np.mean([i for i in range(len(trace.packets)) if socket.inet_ntoa(trace.packets[i][1].src) == trace.sender])
    std_outgoing_ordering = np.std([i for i in range(len(trace.packets)) if socket.inet_ntoa(trace.packets[i][1].src) == trace.sender])
    return(
        Data(
        label=trace.grid,
        num_outgoing=outgoing_packets,
        num_incoming=incoming_packets,
        total_packets=total_packets,
        outgoing_ratio=outgoing_ratio,
        incoming_ratio=incoming_ratio,
        outgoing_bytes=outgoing_bytes,
        incoming_bytes=incoming_bytes,
        avg_outgoing_bytes=avg_outgoing_byte,
        avg_incoming_bytes=avg_incoming_byte,
        std_outgoing_bytes=std_outgoing_byte,
        std_incoming_bytes=std_incoming_byte,
        max_outgoing_bytes=max_outgoing_byte,
        max_incoming_bytes=max_incoming_byte,
        min_outgoing_bytes=min_outgoing_byte,
        min_incoming_bytes=min_incoming_byte,
        avg_outgoing_freq=average_outgoing_freq,
        avg_incoming_freq=average_incoming_freq,
        std_outgoing_freq=std_outgoing_freq,
        std_incoming_freq=std_incoming_freq,
        max_outgoing_freq=max_outgoing_freq,
        max_incoming_freq=max_incoming_freq,
        min_outgoing_freq=min_outgoing_freq,
        min_incoming_freq=min_incoming_freq,
        avg_outgoing_ordering=avg_outgoing_ordering,
        std_outgoing_ordering=std_outgoing_ordering,
        )
    )

def get_training_data_from_traces(traces):
    """
    Takes a dict of traces and returns a list of Data objects
    """
    data = []
    for grid, traces in traces.items():
        for trace in traces:
            data.append(feature_extraction(trace).to_numpy())
    return data

def get_saved_training_data():
    """
    Reads the data written in ./data/extracted_features_per_grid

    Returns: NP array of Data objects
    """

    # get the files in the dir
    files = glob("./data/extracted_features_per_grid/grid-*.npy")
    # if there are no files, throw an error
    if len(files) == 0:
        raise Exception("No files found in ./data/extracted_features_per_grid, has data_collect.py & data_sanitize.py been run?")
    # read the files
    data = []
    for file in tqdm(files, desc="Reading saved data"):
        data.append(np.load(file, allow_pickle=True))
    # return the data
    return np.concatenate(data)

if __name__ == "__main__":
    #logger.log(len(glob('./data/*')))
    traces = get_traces()
    for grid, traces in traces.items():
        data_for_grid = []
        for trace in traces:
            data_for_grid.append(feature_extraction(trace).to_numpy())
        # save this data to a file
        # create dir if not exists
        if not os.path.exists("./data/extracted_features_per_grid"):
            os.makedirs("./data/extracted_features_per_grid")
        np.save(f"./data/extracted_features_per_grid/grid-{grid}.npy", np.array(data_for_grid))
    exit(1)
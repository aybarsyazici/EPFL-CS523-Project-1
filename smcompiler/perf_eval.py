"""
This file includes the tests to measure the communication and computation costs of the
smc protocol implemented for the project.
"""

import time
from multiprocessing import Process, Queue

import pytest

from expression import Scalar, Secret
from protocol import ProtocolSpec
from server import run

from smc_party import SMCParty

def smc_client(client_id, prot, value_dict, queue):
    cli = SMCParty(
        client_id,
        "localhost",
        8000,
        protocol_spec=prot,
        value_dict=value_dict
    )
    res = cli.run()
    queue.put(res)
    print(f"{client_id} has finished!")


def smc_server(args):
    run("localhost", 8000, args)


def run_processes(server_args, *client_args):
    queue = Queue()

    server = Process(target=smc_server, args=(server_args,))
    clients = [Process(target=smc_client, args=(*args, queue)) for args in client_args]
    bytes_sent = []
    bytes_received = []
    computation_time = []

    server.start()
    time.sleep(3)
    for client in clients:
        client.start()

    results = list()
    for client in clients:
        client.join()

    for client in clients:
        result, b_out, b_in, t_comp = queue.get()
        results.append(result)
        bytes_sent.append(b_out)
        bytes_received.append(b_in)
        computation_time.append(t_comp)


    server.terminate()
    server.join()

    # To "ensure" the workers are dead.
    time.sleep(2)

    print("Server stopped.")
    return results, bytes_sent, bytes_received, computation_time


def suite(parties, expr, expected):
    participants = list(parties.keys())
    prot = ProtocolSpec(expr=expr, participant_ids=participants)
    clients = [(name, prot, value_dict) for name, value_dict in parties.items()]

    results, bytes_sent, bytes_received, computation_time = run_processes(participants, *clients)

    for i in range(len(results)):
        print(f"Result: {results[i]} (expected: {expected})")
        print(f"Computation Time: {computation_time[i]}")
        print(f"Bytes Sent: {bytes_sent[i]}")
        print(f"Bytes Received: {bytes_received[i]}")

        assert results[i] == expected


def test_suite1():
    """
    f(a, b, c) = a + b + c
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    expr = (alice_secret + bob_secret + charlie_secret)
    expected = 3 + 14 + 2
    suite(parties, expr, expected)


def test1():
    pass


def test2():
    pass


def test3():
    pass



tests_comm = [test1, test2, test3]
tests = [test_suite1]
if __name__ == "__main__":
    for test in tests:
        test()
        print(f"{test} has passed")


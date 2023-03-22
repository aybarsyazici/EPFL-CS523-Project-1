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

    f(a1, a2, a3, b1, b2, b3, b4, b5, b6, c) = a2+(c* (8 + ((a1 - b1 * a3) + 3*(a2 + b2) * 2*(a3 - b3) + 10 - ((b4 * b5) + (b6 - c)))))
    
    """
    alice_secrets = [Secret(), Secret(), Secret()]
    bob_secrets = [Secret(), Secret(), Secret(), Secret(), Secret(), Secret()]
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secrets[0]: 3, alice_secrets[1]: 57, alice_secrets[2]: 43},
        "Bob": {bob_secrets[0]: 14, bob_secrets[1]: 2, bob_secrets[2]: 5, bob_secrets[3]: 7, bob_secrets[4]: 9, bob_secrets[5]: 11},
        "Charlie": {charlie_secret: 2}
    }
    expr = (
        alice_secrets[1] + 
            (charlie_secret * 
                (Scalar(8) + ((alice_secrets[0] - bob_secrets[0] * alice_secrets[2]) + Scalar(3) * (alice_secrets[1] + bob_secrets[1]) * Scalar(2) * (bob_secrets[2] - alice_secrets[2]) + Scalar(10) - ((bob_secrets[3] * bob_secrets[4]) + (charlie_secret - bob_secrets[5] )))))
    )
    expected = 57 + (2 * (8 + ((3 - 14 * 43) + 3 * (57 + 2) * 2 * (5 - 43) + 10 - ((7 * 9) + (2 - 11)))))
    suite(parties, expr, expected)

"""
Test cases for party count variable
#1: 2 parties, 6 secrets per party
#2: 3 parties, 4 secrets per party
#3: 4 parties, 3 secrets per party
#4: 6 parties, 2 secrets per party
#5: 12 parties, 1 secret per party
expr: (s1 + 5) * (8 - s2) + (s3 * 2) - (s4 - s5) * s6 - s7 + (11 * 6) + (99 - 6*s8) - s9 + s10 * (s11 - s12)
"""
#
def pc_test1():

    p1_secrets = [Secret(), Secret(), Secret(), Secret(), Secret(), Secret()]
    p2_secrets = [Secret(), Secret(), Secret(), Secret(), Secret(), Secret()]
    
    parties = {
        "p1": {p1_secrets[0]: 13, p1_secrets[1]: 10, p1_secrets[2]: 20, p1_secrets[3]: 17, p1_secrets[4]: 9, p1_secrets[5]: 11},
        "p2": {p2_secrets[0]: 8, p2_secrets[1]: 16, p2_secrets[2]: 14, p2_secrets[3]: 12, p2_secrets[4]: 2, p2_secrets[5]: 9},
    }

    expr = (p1_secrets[0] + Scalar(5)) * (Scalar(8) - p2_secrets[0]) + (p1_secrets[1] * Scalar(2)) - (p2_secrets[1] - p1_secrets[2]) * p2_secrets[2] - p1_secrets[3] + (Scalar(11) * Scalar(6)) + (Scalar(99) - Scalar(6)*p2_secrets[3]) - p1_secrets[4] + p2_secrets[4] * (p1_secrets[5] - p2_secrets[5])
    expected = (13 + 5) * (8 - 8) + (10 * 2) - (16 - 20) * 14 - 17 + (11 * 6) + (99 - 6*12) - 9 + 2 * (11 - 9)
    suite(parties, expr, expected)


def pc_test2():
    p1_secrets = [Secret(), Secret(), Secret(), Secret()]
    p2_secrets = [Secret(), Secret(), Secret(), Secret()]
    p3_secrets = [Secret(), Secret(), Secret(), Secret()]

    parties = {
        "p1": {p1_secrets[0]: 13, p1_secrets[1]: 16, p1_secrets[2]: 17, p1_secrets[3]: 2},
        "p2": { p2_secrets[0]: 8, p2_secrets[1]: 20, p2_secrets[2]: 12, p2_secrets[3]: 11},
        "p3": { p3_secrets[0]: 10, p3_secrets[1]: 14, p3_secrets[2]: 9, p3_secrets[3]: 9}
    }

    expr = (p1_secrets[0] + Scalar(5)) * (Scalar(8) - p2_secrets[0]) + (p3_secrets[0] * Scalar(2)) - (p1_secrets[1] - p2_secrets[1]) * p3_secrets[1] - p1_secrets[2] + (Scalar(11) * Scalar(6)) + (Scalar(99) - Scalar(6)*p2_secrets[2]) - p3_secrets[2] + p1_secrets[3] * (p2_secrets[3] - p3_secrets[3])
    expected = (13 + 5) * (8 - 8) + (10 * 2) - (16 - 20) * 14 - 17 + (11 * 6) + (99 - 6*12) - 9 + 2 * (11 - 9)
    suite(parties, expr, expected)


def pc_test3():
    p1_secrets = [Secret(), Secret(), Secret()]
    p2_secrets = [Secret(), Secret(), Secret()]
    p3_secrets = [Secret(), Secret(), Secret()]   
    p4_secrets = [Secret(), Secret(), Secret()]

    parties = {
        "p1": {p1_secrets[0]: 13, p1_secrets[1]: 20, p1_secrets[2]: 9},
        "p2": { p2_secrets[0]: 8, p2_secrets[1]: 14, p2_secrets[2]: 2},
        "p3": { p3_secrets[0]: 10, p3_secrets[1]: 17, p3_secrets[2]: 11},
        "p4": { p4_secrets[0]: 16, p4_secrets[1]: 12, p4_secrets[2]: 9},
    }

    expr = (p1_secrets[0] + Scalar(5)) * (Scalar(8) - p2_secrets[0]) + (p3_secrets[0] * Scalar(2)) - (p4_secrets[0] - p1_secrets[1]) * p2_secrets[1] - p3_secrets[1] + (Scalar(11) * Scalar(6)) + (Scalar(99) - Scalar(6)*p4_secrets[1]) - p1_secrets[2] + p2_secrets[2] * (p3_secrets[2] - p4_secrets[2])
    expected = (13 + 5) * (8 - 8) + (10 * 2) - (16 - 20) * 14 - 17 + (11 * 6) + (99 - 6*12) - 9 + 2 * (11 - 9)

    suite(parties, expr, expected)


def pc_test4():
    pass

def pc_test5():
    pass




tests_party_count = [pc_test1, pc_test2, pc_test3]#, pc_test2, pc_test3]
tests = [test_suite1]

if __name__ == "__main__":
    for test in tests_party_count:
        test()
        print(f"{test} has passed")


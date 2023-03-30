"""
This file includes the tests to measure the communication and computation costs of the
smc protocol implemented for the project.
"""

import time
from multiprocessing import Process, Queue
import numpy as np
import pytest
import random
import sys
import os
sys.setrecursionlimit(5000)


from expression import Scalar, Secret
from protocol import ProtocolSpec
from server import run

from smc_party import SMCParty

default_q = 520633 

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

def mean(arr):
    return sum(arr)/len(arr)

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
    
    return mean(bytes_sent), mean(bytes_received), mean(computation_time)


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
    return suite(parties, expr, expected)

"""
Test cases for party count variable
#1: 2 parties, 25 secrets per party
#2: 5 parties, 10 secrets per party
#3: 10 parties, 5 secrets per party
#4: 25 parties, 2 secrets per party
#5: 50 parties, 1 secret per party
expr: (s1 + 5) * (8 - s2) + (s3 * 2) - (s4 - s5) * s6 - s7 + (11 * 6) + (99 - 6*s8) - s9 + s10 * (s11 - s12)
"""
"""
def party_count_test1_old():

    p1_secrets = [Secret(), Secret(), Secret(), Secret(), Secret(), Secret()]
    p2_secrets = [Secret(), Secret(), Secret(), Secret(), Secret(), Secret()]
    
    parties = {
        "p1": {p1_secrets[0]: 13, p1_secrets[1]: 10, p1_secrets[2]: 20, p1_secrets[3]: 17, p1_secrets[4]: 9, p1_secrets[5]: 11},
        "p2": {p2_secrets[0]: 8, p2_secrets[1]: 16, p2_secrets[2]: 14, p2_secrets[3]: 12, p2_secrets[4]: 2, p2_secrets[5]: 9},
    }

    expr = (p1_secrets[0] + Scalar(5)) * (Scalar(8) - p2_secrets[0]) + (p1_secrets[1] * Scalar(2)) - (p2_secrets[1] - p1_secrets[2]) * p2_secrets[2] - p1_secrets[3] + (Scalar(11) * Scalar(6)) + (Scalar(99) - Scalar(6)*p2_secrets[3]) - p1_secrets[4] + p2_secrets[4] * (p1_secrets[5] - p2_secrets[5])
    expected = (13 + 5) * (8 - 8) + (10 * 2) - (16 - 20) * 14 - 17 + (11 * 6) + (99 - 6*12) - 9 + 2 * (11 - 9)
    suite(parties, expr, expected % default_q)


def party_count_test2_old():
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
    suite(parties, expr, expected % default_q)


def party_count_test3_old():
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

    suite(parties, expr, expected % default_q)


def party_count_test4_old():
    p1_secrets = [Secret(), Secret()]
    p2_secrets = [Secret(), Secret()]
    p3_secrets = [Secret(), Secret()]   
    p4_secrets = [Secret(), Secret()]
    p5_secrets = [Secret(), Secret()]   
    p6_secrets = [Secret(), Secret()]

    parties = {
        "p1": {p1_secrets[0]: 13, p1_secrets[1]: 17},
        "p2": { p2_secrets[0]: 8, p2_secrets[1]: 12},
        "p3": { p3_secrets[0]: 10, p3_secrets[1]: 9},
        "p4": { p4_secrets[0]: 16, p4_secrets[1]: 2},
        "p5": { p5_secrets[0]: 20, p5_secrets[1]: 11},
        "p6": { p6_secrets[0]: 14, p6_secrets[1]: 9}
    }

    expr = (p1_secrets[0] + Scalar(5)) * (Scalar(8) - p2_secrets[0]) + (p3_secrets[0] * Scalar(2)) - (p4_secrets[0] - p5_secrets[0]) * p6_secrets[0] - p1_secrets[1] + (Scalar(11) * Scalar(6)) + (Scalar(99) - Scalar(6)*p2_secrets[1]) - p3_secrets[1] + p4_secrets[1] * (p5_secrets[1] - p6_secrets[1])
    expected = (13 + 5) * (8 - 8) + (10 * 2) - (16 - 20) * 14 - 17 + (11 * 6) + (99 - 6*12) - 9 + 2 * (11 - 9)

    suite(parties, expr, expected % default_q)

def party_count_test5_old():
    p1_secret = Secret()
    p2_secret = Secret()
    p3_secret = Secret()
    p4_secret = Secret()
    p5_secret = Secret()
    p6_secret = Secret()
    p7_secret = Secret()
    p8_secret = Secret()
    p9_secret = Secret()
    p10_secret = Secret()
    p11_secret = Secret()
    p12_secret = Secret()

    parties = {
        "p1": {p1_secret: 13},
        "p2": { p2_secret: 8},
        "p3": { p3_secret: 10},
        "p4": { p4_secret: 16},
        "p5": { p5_secret: 20},
        "p6": { p6_secret: 14},
        "p7": {p7_secret: 17},
        "p8": { p8_secret: 12},
        "p9": { p9_secret: 9},
        "p10": { p10_secret: 2},
        "p11": { p11_secret: 11},
        "p12": { p12_secret: 9}
    }

    expr = (p1_secret + Scalar(5)) * (Scalar(8) - p2_secret) + (p3_secret * Scalar(2)) - (p4_secret - p5_secret) * p6_secret - p7_secret + (Scalar(11) * Scalar(6)) + (Scalar(99) - Scalar(6)*p8_secret) - p9_secret + p10_secret * (p11_secret - p12_secret)
    expected = (13 + 5) * (8 - 8) + (10 * 2) - (16 - 20) * 14 - 17 + (11 * 6) + (99 - 6*12) - 9 + 2 * (11 - 9)

    suite(parties, expr, expected % default_q)
"""

def parties_test(party_count):
    secrets_per_party = int(50/party_count)

    secrets = []
    for i in range(party_count):
        secrets.append([Secret() for _ in range(secrets_per_party)])

    parties = {}
    expected = 0
    for i in range(party_count):
        ps = "p" + str(i+1)
        parties[ps] = {}
        for j in range(secrets_per_party):
            v = random.randint(1,10)
            parties[ps][secrets[i][j]] = v
            expected += v

    expr = Scalar(0)

    for i in range(party_count):
        for j in range(secrets_per_party):
            expr += secrets[i][j]
 
    return suite(parties, expr, expected % default_q)

def parties_test2(party_count):
    secrets_per_party = 1

    secrets = []
    for i in range(party_count):
        secrets.append([Secret() for _ in range(secrets_per_party)])

    parties = {}
    expected = 0
    for i in range(party_count):
        ps = "p" + str(i+1)
        parties[ps] = {}
        for j in range(secrets_per_party):
            v = random.randint(1,10)
            parties[ps][secrets[i][j]] = v
            expected += v

    expr = Scalar(0)

    for i in range(party_count):
        for j in range(secrets_per_party):
            expr += secrets[i][j]
 
    return suite(parties, expr, expected % default_q)    


def secret_addition_test(s):
    p1_secrets = [Secret() for _ in range(s)]
    p2_secrets = [Secret() for _ in range(s)]
    p3_secrets = [Secret() for _ in range(s)]
    p4_secrets = [Secret() for _ in range(s)]
    p5_secrets = [Secret() for _ in range(s)]
    
    parties = {}
    parties["p1"] = {}
    parties["p2"] = {}
    parties["p3"] = {}
    parties["p4"] = {}
    parties["p5"] = {}

    expected = 0

    for i in range(s):
        r1, r2, r3, r4, r5 = random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)
        expected += r1 + r2 + r3 + r4 + r5
        parties["p1"][p1_secrets[i]] = r1
        parties["p2"][p2_secrets[i]] = r2
        parties["p3"][p3_secrets[i]] = r3
        parties["p4"][p4_secrets[i]] = r4
        parties["p5"][p5_secrets[i]] = r5

    expr = Scalar(0)
    for i in range(s):
        expr += p1_secrets[i] + p2_secrets[i] + p3_secrets[i] + p4_secrets[i] + p5_secrets[i]

    return suite(parties, expr, expected % default_q)

def scalar_addition_test(s):
    p1_secret = Secret()
    p2_secret = Secret()
    p3_secret = Secret()
    p4_secret = Secret()
    p5_secret = Secret()

    parties = {}
    parties["p1"] = {}
    parties["p2"] = {}
    parties["p3"] = {}
    parties["p4"] = {}
    parties["p5"] = {}

    expected = 0
    
    r1, r2, r3, r4, r5 = random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)
    expected += r1 + r2 + r3 + r4 + r5
    parties["p1"][p1_secret] = r1
    parties["p2"][p2_secret] = r2
    parties["p3"][p3_secret] = r3
    parties["p4"][p4_secret] = r4
    parties["p5"][p5_secret] = r5

    expr = Scalar(0)
    expr += p1_secret + p2_secret + p3_secret + p4_secret + p5_secret
    
    for _ in range(s):
        scalar = random.randint(1,10)
        expr += Scalar(scalar)
        expected += scalar

    return suite(parties, expr, expected % default_q)

def scalar_mult_test(s):
    p1_secret = Secret()
    p2_secret = Secret()
    p3_secret = Secret()
    p4_secret = Secret()
    p5_secret = Secret()

    parties = {}
    parties["p1"] = {}
    parties["p2"] = {}
    parties["p3"] = {}
    parties["p4"] = {}
    parties["p5"] = {}

    expected = 1
    
    r1, r2, r3, r4, r5 = random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)
    expected *= r1 * r2 * r3 * r4 * r5
    parties["p1"][p1_secret] = r1
    parties["p2"][p2_secret] = r2
    parties["p3"][p3_secret] = r3
    parties["p4"][p4_secret] = r4
    parties["p5"][p5_secret] = r5

    expr = Scalar(1)
    expr *= p1_secret * p2_secret * p3_secret * p4_secret * p5_secret
    
    for _ in range(s):
        scalar = random.randint(1,10)
        expr *= Scalar(scalar)
        expected *= scalar

    return suite(parties, expr, expected % default_q)

def secret_mult_test(s):
    p1_secrets = [Secret() for _ in range(s)]
    p2_secrets = [Secret() for _ in range(s)]
    p3_secrets = [Secret() for _ in range(s)]
    p4_secrets = [Secret() for _ in range(s)]
    p5_secrets = [Secret() for _ in range(s)]    

    parties = {}
    parties["p1"] = {}
    parties["p2"] = {}
    parties["p3"] = {}
    parties["p4"] = {}
    parties["p5"] = {}    

    expected = 1

    for i in range(s):
        r1, r2, r3, r4, r5 = random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)
        expected *= (r1 * r2 * r3 * r4 * r5) 
        parties["p1"][p1_secrets[i]] = r1
        parties["p2"][p2_secrets[i]] = r2
        parties["p3"][p3_secrets[i]] = r3
        parties["p4"][p4_secrets[i]] = r4
        parties["p5"][p5_secrets[i]] = r5

    expr = Scalar(1)
    for i in range(s):
        expr *= p1_secrets[i] * p2_secrets[i] * p3_secrets[i] * p4_secrets[i] * p5_secrets[i]
    return suite(parties, expr, expected % default_q)    

tests = [parties_test]

def test_cases_parties():
    params = [2, 5, 10, 25, 50]
    os.chdir("eval_results")

    for p in params:
        bytes_sent = []
        bytes_received = []
        computation_time = []
        filename = f'parties_{p}.txt'
        f = open(filename, "w")
        for i in range(30):
            b_out, b_in, t = parties_test(p)
            bytes_sent.append(b_out)
            bytes_received.append(b_in)
            computation_time.append(t)
            f.write(f'Run {str(i+1)}: \n')
            f.write(f'\tBytes sent: {b_out}\n')
            f.write(f'\tBytes received: {b_in}\n')
            f.write(f'\tRuntime: {t}\n')
        f.write(f'On average: \n')
        f.write(f'\tBytes sent => Mean: {mean(bytes_sent)}, Std Dev: {np.std(bytes_sent)} \n')
        f.write(f'\tBytes received => Mean: {mean(bytes_received)}, Std Dev: {np.std(bytes_received)} \n')
        f.write(f'\tRuntime => Mean: {mean(computation_time)}, Std Dev: {np.std(computation_time)}\n')   
    f.close()

def test_cases_parties2():
    params = [2, 5, 10, 25, 50]
    os.chdir("eval_results")

    for p in params:
        bytes_sent = []
        bytes_received = []
        computation_time = []
        filename = f'parties2_{p}.txt'
        f = open(filename, "w")
        for i in range(30):
            b_out, b_in, t = parties_test2(p)
            bytes_sent.append(b_out)
            bytes_received.append(b_in)
            computation_time.append(t)
            f.write(f'Run {str(i+1)}: \n')
            f.write(f'\tBytes sent: {b_out}\n')
            f.write(f'\tBytes received: {b_in}\n')
            f.write(f'\tRuntime: {t}\n')
        f.write(f'On average: \n')
        f.write(f'\tBytes sent => Mean: {mean(bytes_sent)}, Std Dev: {np.std(bytes_sent)} \n')
        f.write(f'\tBytes received => Mean: {mean(bytes_received)}, Std Dev: {np.std(bytes_received)} \n')
        f.write(f'\tRuntime => Mean: {mean(computation_time)}, Std Dev: {np.std(computation_time)}\n')   
    f.close()    

def test_cases_secret_add():
    params = [1, 10, 50, 100, 200]
    os.chdir("eval_results")

    for p in params:
        bytes_sent = []
        bytes_received = []
        computation_time = []
        filename = f'secret_add_{p}.txt'
        f = open(filename, "w")
        for i in range(30):
            b_out, b_in, t = secret_addition_test(p)
            bytes_sent.append(b_out)
            bytes_received.append(b_in)
            computation_time.append(t)
            f.write(f'Run {str(i+1)}: \n')
            f.write(f'\tBytes sent: {b_out}\n')
            f.write(f'\tBytes received: {b_in}\n')
            f.write(f'\tRuntime: {t}\n')
        f.write(f'On average: \n')
        f.write(f'\tBytes sent => Mean: {mean(bytes_sent)}, Std Dev: {np.std(bytes_sent)} \n')
        f.write(f'\tBytes received => Mean: {mean(bytes_received)}, Std Dev: {np.std(bytes_received)} \n')
        f.write(f'\tRuntime => Mean: {mean(computation_time)}, Std Dev: {np.std(computation_time)}\n')  
    f.close()

def test_cases_scalar_add():
    params = [5, 50, 100, 200, 500]
    os.chdir("eval_results")

    for p in params:
        bytes_sent = []
        bytes_received = []
        computation_time = []
        filename = f'scalar_add_{p}.txt'
        f = open(filename, "w")
        for i in range(30):
            b_out, b_in, t = scalar_addition_test(p)
            bytes_sent.append(b_out)
            bytes_received.append(b_in)
            computation_time.append(t)
            f.write(f'Run {str(i+1)}: \n')
            f.write(f'\tBytes sent: {b_out}\n')
            f.write(f'\tBytes received: {b_in}\n')
            f.write(f'\tRuntime: {t}\n')
        f.write(f'On average: \n')
        f.write(f'\tBytes sent => Mean: {mean(bytes_sent)}, Std Dev: {np.std(bytes_sent)} \n')
        f.write(f'\tBytes received => Mean: {mean(bytes_received)}, Std Dev: {np.std(bytes_received)} \n')
        f.write(f'\tRuntime => Mean: {mean(computation_time)}, Std Dev: {np.std(computation_time)}\n')  
    f.close()

def test_cases_secret_mult():
    params = [10, 200]
    os.chdir("eval_results")

    for p in params:
        bytes_sent = []
        bytes_received = []
        computation_time = []
        filename = f'secret_mult_{p}.txt'
        f = open(filename, "w")
        for i in range(30):
            b_out, b_in, t = secret_mult_test(p)
            bytes_sent.append(b_out)
            bytes_received.append(b_in)
            computation_time.append(t)
            f.write(f'Run {str(i+1)}: \n')
            f.write(f'\tBytes sent: {b_out}\n')
            f.write(f'\tBytes received: {b_in}\n')
            f.write(f'\tRuntime: {t}\n')
        f.write(f'On average: \n')
        f.write(f'\tBytes sent => Mean: {mean(bytes_sent)}, Std Dev: {np.std(bytes_sent)} \n')
        f.write(f'\tBytes received => Mean: {mean(bytes_received)}, Std Dev: {np.std(bytes_received)} \n')
        f.write(f'\tRuntime => Mean: {mean(computation_time)}, Std Dev: {np.std(computation_time)}\n')  
    f.close()

def test_cases_scalar_mult():
    params = [5, 50, 100, 200, 500]
    os.chdir("eval_results")

    for p in params:
        bytes_sent = []
        bytes_received = []
        computation_time = []
        filename = f'scalar_mult_{p}.txt'
        f = open(filename, "w")
        for i in range(30):
            b_out, b_in, t = scalar_mult_test(p)
            bytes_sent.append(b_out)
            bytes_received.append(b_in)
            computation_time.append(t)
            f.write(f'Run {str(i+1)}: \n')
            f.write(f'\tBytes sent: {b_out}\n')
            f.write(f'\tBytes received: {b_in}\n')
            f.write(f'\tRuntime: {t}\n')
        f.write(f'On average: \n')
        f.write(f'\tBytes sent => Mean: {mean(bytes_sent)}, Std Dev: {np.std(bytes_sent)} \n')
        f.write(f'\tBytes received => Mean: {mean(bytes_received)}, Std Dev: {np.std(bytes_received)} \n')
        f.write(f'\tRuntime => Mean: {mean(computation_time)}, Std Dev: {np.std(computation_time)}\n')  
    f.close()

if __name__ == "__main__":
    secret_addition_test(3)


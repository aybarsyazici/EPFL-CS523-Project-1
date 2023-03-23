"""
Integration tests that verify different aspects of the protocol.
You can *add* new tests here, but it is best to  add them to a new test file.

ALL EXISTING TESTS IN THIS SUITE SHOULD PASS WITHOUT ANY MODIFICATION TO THEM.
"""

from functools import reduce
import random
import time
from multiprocessing import Process, Queue
import pytest
from secret_sharing import default_q
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

    server.start()
    time.sleep(3)
    for client in clients:
        client.start()

    results = list()
    for client in clients:
        client.join()

    for client in clients:
        results.append(queue.get())

    server.terminate()
    server.join()

    # To "ensure" the workers are dead.
    time.sleep(2)

    print("Server stopped.")

    return results


def suite(parties, expr, expected):
    participants = list(parties.keys())
    prot = ProtocolSpec(expr=expr, participant_ids=participants)
    clients = [(name, prot, value_dict) for name, value_dict in parties.items()]

    results = run_processes(participants, *clients)

    for result in results:
        print(f"Result: {result} (expected: {expected})")
        assert result == expected


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



def test_suite2():
    """
    f(a, b) = a - b
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 14},
        "Bob": {bob_secret: 3},
    }

    expr = (alice_secret - bob_secret)
    expected = 14 -3
    suite(parties, expr, expected)


def test_suite3():
    """
    f(a, b, c) = (a + b + c) ∗ K
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    expr = ((alice_secret + bob_secret + charlie_secret) * Scalar(5))
    expected = (3 + 14 + 2) * 5
    suite(parties, expr, expected)


def test_suite4():
    """
    f(a, b, c) = (a + b + c) + K
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    expr = ((alice_secret + bob_secret + charlie_secret) + Scalar(5))
    expected = (3 + 14 + 2) + 5
    suite(parties, expr, expected)


def test_suite5():
    """
    f(a, b, c) = (a ∗ K0 + b - c) + K1
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    expr = (((alice_secret * Scalar(5)) + bob_secret - charlie_secret) + Scalar(9))
    expected = ((3 * 5) + 14 - 2) + 9
    suite(parties, expr, expected)


def test_suite6():
    """
    f(a, b, c, d) = a + b + c + d
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()
    david_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2},
        "David": {david_secret: 5}
    }

    expr = (alice_secret + bob_secret + charlie_secret + david_secret)
    expected = 3 + 14 + 2 + 5
    suite(parties, expr, expected)


def test_suite7():
    """
    f(a, b, c) = (a ∗ b) + (b ∗ c) + (c ∗ a)
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    expr = (
        (alice_secret * bob_secret) +
        (bob_secret * charlie_secret) +
        (charlie_secret * alice_secret)
    )
    expected = ((3 * 14) + (14 * 2) + (2 * 3))
    suite(parties, expr, expected)


def test_suite8():
    """
    f(a, b, c, d, e) = ((a + K0) + b ∗ K1 - c) ∗ (d + e)
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()
    david_secret = Secret()
    elusinia_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2},
        "David": {david_secret: 5},
        "Elusinia": {elusinia_secret: 7}
    }

    expr = (
        (
            (alice_secret + Scalar(8)) +
            ((bob_secret * Scalar(9)) - charlie_secret)
         ) * (david_secret + elusinia_secret)
    )
    expected = (((3 + 8) + (14 * 9) - 2) * (5 + 7))
    suite(parties, expr, expected)


def test_suite9():
    """
    f(a1, a2, a3, b) = a1 + a2 + a3 + b
    """
    alice_secrets = [Secret(), Secret(), Secret()]
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secrets[0]: 3, alice_secrets[1]: 14, alice_secrets[2]: 2},
        "Bob": {bob_secret: 5},
    }

    expr = alice_secrets[0] + alice_secrets[1] + alice_secrets[2] + bob_secret
    expected = 3 + 14 + 2 + 5
    suite(parties, expr, expected)


def test_suite10():
    """
    f(a, b) = a * b * (15 + 15 * 3)
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 5},
    }

    expr = alice_secret + bob_secret * (Scalar(15) + Scalar(15) * Scalar(3))
    expected = 3 + 5 * (15 + 15 * 3)
    suite(parties, expr, expected)

def test_suite11():
    """
    f(a, b) = a - b + c - d
    """
    alice_secret = Secret()
    bob_secret = Secret()
    can_secret = Secret()
    aybars_secret = Secret()

    parties = {
        "Alice": {alice_secret: 14},
        "Bob": {bob_secret: 3},
        "Can": {can_secret: 5},
        "Aybars": {aybars_secret: 7}
    }

    expr = (alice_secret - bob_secret + can_secret - aybars_secret)
    expected = 14 - 3 + 5 - 7
    suite(parties, expr, expected)

def test_suite12():
    """
    f(a, b) = a - b - c + d
    """
    alice_secret = Secret()
    bob_secret = Secret()
    can_secret = Secret()
    aybars_secret = Secret()

    parties = {
        "Alice": {alice_secret: 14},
        "Bob": {bob_secret: 3},
        "Can": {can_secret: 5},
        "Aybars": {aybars_secret: 7}
    }

    expr = (alice_secret - bob_secret + can_secret - aybars_secret)
    expected = 14 - 3 + 5 - 7
    suite(parties, expr, expected)

def test_suite7_modified():
    """
    f(a, b, c) = (a ∗ b) + (a * b) + ((b ∗ c) + (b * c) - ((c ∗ a) + (c * a))) + (a ∗ a)
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    expr = (
        (alice_secret * bob_secret) + (alice_secret * bob_secret) +
        ((bob_secret * charlie_secret) + (bob_secret * charlie_secret) -
        ((charlie_secret * alice_secret) + (charlie_secret * alice_secret)))
        + (alice_secret * alice_secret)
    )
    expected = ((3 * 14) + (3 * 14) + ((14 * 2) + (14 * 2) - ((2 * 3) + (2 * 3))) + (3 * 3))
    suite(parties, expr, expected)

def simple_custom_test():
    """
    f(a,b) = 5*(3 + (a * b))
    
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14}
    }

    expr = Scalar(5)*(Scalar(3) + (alice_secret * bob_secret))
    expected = 5*(3 + (3 * 14))
    suite(parties, expr, expected)

def simple_substraction():
    """
    f(a,b) = (a - 20) + (b-10)
    
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 13},
        "Bob": {bob_secret: 18}
    }

    expr =  (alice_secret -  Scalar(20)) + (bob_secret - Scalar(10))
    expected = (13-20) + (18-10)
    suite(parties, expr, expected)


def simple_substraction_2():
    """
    f(a,b) = (a - 10) + (b-10)
    
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 13},
        "Bob": {bob_secret: 18}
    }

    expr =  (alice_secret -  Scalar(10)) * (bob_secret - Scalar(10))
    expected = (13-10) * (18-10)
    suite(parties, expr, expected)

def simple_substraction_3():
    """
    f(a,b) = (10 - a) + (10 - b)
    
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 8}
    }

    expr =  (Scalar(10) - alice_secret) + (Scalar(10) - bob_secret)
    expected = (10-3) + (10 - 8)
    suite(parties, expr, expected)

def simple_substraction_4():
    """
    f(a,b) = (10 - a) * (10 - b)
    
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 8}
    }

    expr =  (Scalar(10) - alice_secret) * (Scalar(10) - bob_secret)
    expected = (10-3) * (10 - 8)
    suite(parties, expr, expected)

def simple_substraction_5():
    """
    f(a,b) = (a - 10) * (b - 10)
    
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 8}
    }

    expr =  (alice_secret - Scalar(10)) * (bob_secret - Scalar(10))
    expected = (3-10) * (8 - 10)
    suite(parties, expr, expected)

def test_multi_secret_1():
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
        alice_secrets[1] + (charlie_secret * (Scalar(8) + ((alice_secrets[0] - bob_secrets[0] * alice_secrets[2]) + Scalar(3) * (alice_secrets[1] + bob_secrets[1]) * Scalar(2) * (alice_secrets[2] - bob_secrets[2]) + Scalar(10) - ((bob_secrets[3] * bob_secrets[4]) + (bob_secrets[5] - charlie_secret)))))
    )
    expected = 57 + (2 * (8 + ((3 - 14 * 43) + 3 * (57 + 2) * 2 * (43 - 5) + 10 - ((7 * 9) + (11 - 2)))))
    suite(parties, expr, expected)

def test_multi_secret_2():
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


def test_eval_1():

    """ 
    f() = (5 - (5*a1 + 9 - (3*b1 + b2*(6 - a2) + (c2*c1) - (a3*5))))
    """

    alice_secrets = [Secret(), Secret(), Secret()]
    bob_secrets = [Secret(), Secret()]
    charlie_secrets = [Secret(),Secret()]

    parties = {
        "Alice": {alice_secrets[0]: 3, alice_secrets[1]: 57, alice_secrets[2]: 43},
        "Bob": {bob_secrets[0]: 14, bob_secrets[1]: 2},
        "Charlie": {charlie_secrets[0]: 12,charlie_secrets[1]: 9 }
    }

    expr = (Scalar(5) - (Scalar(5)*alice_secrets[0] + Scalar(9) - (Scalar(3)*bob_secrets[0] + bob_secrets[1]*(Scalar(6)-alice_secrets[1]) + (charlie_secrets[1]*charlie_secrets[0]) - (alice_secrets[2] * Scalar(5)))))
    expected = (5 - (5*3 + 9 - (3*14 + 2*(6 - 57) + (9*12) - (43*5))))
    suite(parties, expr, expected)


def test_eval_2():
    """
    f() = (a1 * 31 * b1 * 5 * c1 * 44 * d1) * (5 - a2 - 8 + b2 + 99 - c2 - 55 + d2 - 23) 
    """

    walter_secrets = [Secret(), Secret()]
    saul_secrets = [Secret(), Secret()]
    mike_secrets = [Secret(),Secret()]
    gus_secrets = [Secret(), Secret()]

    parties = {
        "Walter": {walter_secrets[0]: 3, walter_secrets[1]: 5},
        "Saul": {saul_secrets[0]: 2, saul_secrets[1]: 2},
        "Mike": {mike_secrets[0]: 1, mike_secrets[1]: 4 },
        "Gus": {gus_secrets[0]: 3, gus_secrets[1]: 2}
    }

    expr = (walter_secrets[0] * Scalar(31) * saul_secrets[0] * Scalar(5) * mike_secrets[0] * Scalar(44) * gus_secrets[0]) * (Scalar(5) - walter_secrets[1] - Scalar(8) + saul_secrets[1] + Scalar(99) - mike_secrets[1] - Scalar(55) + gus_secrets[1] - Scalar(23))
    expected = ( 3 * 31 * 14 * 5 * 12 * 44 * 66) * (5 - 57 - 8 + 2 + 99 - 9 - 55 + 321 - 23) 
    suite(parties, expr, expected)


def test_eval_3():
    """
    f() = (99999 - (a1 - (5 * (a2 + (88 - b1 * (c1 + 7 * (88 - c2)))))))
    """

    walter_secrets = [Secret(), Secret()]
    saul_secrets = [Secret()]
    mike_secrets = [Secret(),Secret()]

    parties = {
        "Walter": {walter_secrets[0]: 9, walter_secrets[1]: 6},
        "Saul": {saul_secrets[0]: 2},
        "Mike": {mike_secrets[0]: 5, mike_secrets[1]: 83 },
    }

    expr = (Scalar(99999) - (walter_secrets[0] - (Scalar(5) * (walter_secrets[1] + (Scalar(88) - saul_secrets[0] * (mike_secrets[0] + Scalar(7) * (Scalar(88) - mike_secrets[1])))))))
    expected = (99999 - (9 - (5 * (6 + (88 - 2 * (5 + 7 * (88 - 83)))))))
    suite(parties, expr, expected)

def test_lots_of_parties():
    """
    f() = (a1 + b1 + c1 + d1 + e1 + f1 + g1 + h1 + i1 + j1 + k1 + l1 + m1 + n1 + o1 + p1 + q1 + r1 + s1 + t1 + u1 + v1 + w1 + x1 + y1 + z1)
    """

    parties = {}
    secrets = []
    for i in range(26):
        secret = Secret()
        parties[chr(ord('a') + i)] = {secret: i}
        secrets.append(secret)
    
    expr = reduce(lambda x, y: x + y, secrets)
    expected = sum(range(26))
    suite(parties, expr, expected)

def test_lots_of_parties_multiplication():
    """
    f() = (a1 * b1 * c1 * d1 * e1 * f1 * g1 * h1 * i1 * j1 * k1 * l1 * m1 * n1 * o1 * p1 * q1 * r1 * s1 * t1 * u1 * v1 * w1 * x1 * y1 * z1)
    """

    parties = {}
    secrets = []
    for i in range(26):
        secret = Secret()
        parties[chr(ord('a') + i)] = {secret: i}
        secrets.append(secret)
    
    expr = reduce(lambda x, y: x * y, secrets)
    expected = reduce(lambda x, y: x * y, range(26))
    suite(parties, expr, expected)

def test_lots_of_parties_multiplication_2():
    """
    f() = (a1 * b1 * c1 * d1 * e1 * f1 * g1 * h1 * i1 * j1 * k1 * l1 * m1 * n1 * o1 * p1 * q1 * r1 * s1 * t1 * u1 * v1 * w1 * x1 * y1 * z1)
    """

    parties = {}
    secrets = []
    for i in range(0,10):
        parties[str(i)] = {}
        for j in range(1,10):
            secret = Secret()
            secrets.append(secret)
            parties[str(i)][secret] = j

    expr = reduce(lambda x, y: x * y, secrets)
    expected = (
        reduce(lambda x, y: x * y, range(1,10)) ** 10
    )
    print('EXPECTED', expected)
    suite(parties, expr, expected % default_q),

def test_small_parties_lots_of_multiplication():
    parties = {}
    secrets = []
    for i in range(0,3):
        parties[str(i)] = {}
        for j in range(1,70):
            secret = Secret()
            secrets.append(secret)
            parties[str(i)][secret] = j

    expr = reduce(lambda x, y: x * y, secrets)
    expected = (
        reduce(lambda x, y: x * y, range(1,70)) ** 3
    )
    suite(parties, expr, expected % default_q)


tests = [
        # test_suite1,
        # test_suite2,
        # test_suite3,
        # test_suite4,
        # test_suite5,
        # test_suite6,
        # test_suite7,
        # test_suite8,
        # test_suite9,
        # test_suite10, 
        # test_suite11,
        # test_suite12,
        # test_suite7_modified,
        # simple_custom_test,
        # simple_substraction,
        # simple_substraction_2,
        # simple_substraction_3,
        # simple_substraction_4,
        # simple_substraction_5,
        # test_multi_secret_1,
        # test_eval_3
        test_lots_of_parties,
        test_lots_of_parties_multiplication,
        test_lots_of_parties_multiplication_2,
        test_small_parties_lots_of_multiplication
        # test_multi_secret_2, This fails saying: Expected -28117 but got 492516. Notice that the expected value is negative. But we operate in Zq(Which is 520633), so -28117mod(520633) = 492516. So the test is correct.
]

# main
if __name__ == "__main__":
    for test in tests:
        test()
        print(f"{test} has passed")

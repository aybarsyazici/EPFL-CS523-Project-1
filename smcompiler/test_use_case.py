from use_case import Student, Class
from multiprocessing import Process, Queue
import pytest
import time

from expression import Scalar, Secret
from server import run
import numpy as np

def smc_client(client_id, cl, value_dict, queue):
    cli = Student(
        client_id,
        "localhost",
        8000,
        cl=cl,
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
    print(results)
    return results


def suite(students, lecture_list, expected):
    student_keys = list(students.keys())
    cl = Class(lectures=lecture_list, students=student_keys)
    clients = [(name, cl, value_dict) for name, value_dict in students.items()]

    results = run_processes(student_keys, *clients)
    index = 0

    first_avg = None
    first_std_dev = None

    for avg, std_dev in results:
        print(f"AVG: {avg}, STD_DEV: {std_dev}")
        # Check if all results are the same
        if first_avg is None:
            first_avg = avg
            first_std_dev = std_dev
        else:
            assert first_avg == avg
            assert first_std_dev == std_dev

    for lecture in expected.keys():
        assert lecture in first_avg.keys()
        print(f"Expected: {expected[lecture]}, Actual: ({first_avg[lecture], first_std_dev[lecture]})")
        assert np.isclose(first_avg[lecture],expected[lecture][0], atol=0.001)
        assert np.isclose(first_std_dev[lecture],expected[lecture][1], atol=0.001)
    


def test_use_case_1():
    alice_secret = Secret(id=b"Maths/Alice")
    bob_secret = Secret(id=b"Maths/Bob")
    charlie_secret = Secret(id=b"Maths/Charlie")

    students = {
        "Alice": {alice_secret: 50},
        "Bob": {bob_secret: 50},
        "Charlie": {charlie_secret: 50}
    }

    excepted = {
        'Maths': (np.mean([50, 50, 50]), np.std([50, 50, 50]))
    }

    suite(students, ['Maths'], expected=excepted)

def test_use_case_2():
    alice_secrets = [Secret(id=b"Maths/Alice"),Secret(id=b"English/Alice"),Secret(id=b"Geography/Alice")]
    bob_secrets = [Secret(id=b"Maths/Bob"), Secret(id=b"English/Bob"), Secret(id=b"Geography/Bob")]
    charlie_secrets = [Secret(id=b"Maths/Charlie"), Secret(id=b"English/Charlie"), Secret(id=b"Geography/Charlie")]

    students = {
        "Alice": {alice_secrets[0]: 100, alice_secrets[1]: 43, alice_secrets[2]: 60},
        "Bob": {bob_secrets[0]: 62, bob_secrets[1]: 36, bob_secrets[2]: 90},
        "Charlie": {charlie_secrets[0]: 83, charlie_secrets[1]: 51, charlie_secrets[2]: 100}
    }
    # Calculate SAMPLE average and standard deviation using numpy
    excepted = {
        'Maths': (np.mean([100, 62, 83]), np.std([100, 62, 83])),
        'English': (np.mean([43, 36, 51]), np.std([43, 36, 51])),
        'Geography': (np.mean([60, 90, 100]), np.std([60, 90, 100]))
    }
    suite(students, ['Maths', 'English', 'Geography'],expected=excepted)

tests = [test_use_case_1, test_use_case_2]

if __name__ == "__main__":
    for test in tests:
        test()
        print(f"Test: {test} passed!")
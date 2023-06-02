import test_registrationscheme
from measurement import Measurement, measured
from stroll import Client, Server
import os
import sys
import statistics as stat
from math import sqrt


def init_measurements():
    measurements = {}
    measurements["Client"] = {"prepare_registration": Measurement(), "process_registration_response": Measurement(), "sign_request": Measurement()}
    measurements["Server"] = {"generate_ca": Measurement(), "process_registration": Measurement(), "check_request_signature": Measurement()}
    measurements["IssueScheme"] = {"sign_issue_request": Measurement(), "create_issue_request": Measurement(), "obtain_credential": Measurement()}
    measurements["SignatureScheme"] = {"generate_key": Measurement()}
    measurements["DisclosureProof"] = {"create_disclosure_proof": Measurement(), "verify_disclosure_proof": Measurement()}
    measurements["ProofHandler"] = {"generate": Measurement(), "verify": Measurement()}
    return measurements

"""
A scenario where three clients and one server are present.
We measure the metrics for one client and the server
"""
def eval_with_three_clients():
    measurements = init_measurements()

    s = Server(measurement_mode=True)
    c1 = Client(measurement_mode=True)
    c2 = Client(measurement_mode=True)
    c3 = Client(measurement_mode=True)

    """
    Simulate a situation where 3 clients interact with the server
    """    
    server_subs = ["hotel", "library", "restaurant", "bar", "dojo", "cafe", "username"]

    #Client with valid subs
    client1_subs = ["library", "restaurant"]
    client1_name = "walter"

    #Client with valid subs
    client2_subs = ["hotel", "library", "restaurant", "bar", "dojo"]
    client2_name = "mike"

    #Client with valid subs
    client3_subs = ["bar", "cafe"]
    client3_name = "gustavo"

    server_sk,server_pk = measured(s.generate_ca, measurements["Server"]["generate_ca"])(server_subs, True, measurements=measurements)

    ######################################
    ##Prepare registration for all clients
    ######################################
    #Valid reg for c1

    issuance_req1, state1 = measured(c1.prepare_registration, measurements["Client"]["prepare_registration"])(
        server_pk, client1_name, client1_subs, measurements=measurements
    )
    assert issuance_req1 is not None

    #Valid reg for c2
    issuance_req2, state2 = measured(c2.prepare_registration, measurements["Client"]["prepare_registration"])(
        server_pk, client2_name, client2_subs, measurements=measurements
    )
    assert issuance_req2 is not None

    #Valid reg for c3
    issuance_req3, state3 = measured(c3.prepare_registration, measurements["Client"]["prepare_registration"])(
        server_pk, client3_name, client3_subs, measurements=measurements
    )
    assert issuance_req3 is not None
    
    ################################################
    ##Process registration by server for all clients
    ################################################
    registration_res1 = measured(s.process_registration, measurements["Server"]["process_registration"])(
        server_sk, server_pk, issuance_req1, client1_name, client1_subs, measurements=measurements
    )
    assert registration_res1 is not None

    registration_res2 = measured(s.process_registration, measurements["Server"]["process_registration"])(
        server_sk, server_pk, issuance_req2, client2_name, client2_subs, measurements=measurements
    )
    assert registration_res2 is not None

    registration_res3 = measured(s.process_registration, measurements["Server"]["process_registration"])(
        server_sk, server_pk, issuance_req3, client3_name, client3_subs, measurements=measurements
    )
    assert registration_res3 is not None

    ################################################
    ##Process registration response for all clients
    ################################################
    credential1 = measured(c1.process_registration_response, measurements["Client"]["process_registration_response"])(
        server_pk, registration_res1, state1, measurements=measurements
    )

    credential2 = measured(c2.process_registration_response, measurements["Client"]["process_registration_response"])(
        server_pk, registration_res2, state2, measurements=measurements
    )

    credential3 = measured(c3.process_registration_response, measurements["Client"]["process_registration_response"])(
        server_pk, registration_res3, state3, measurements=measurements
    )

    lat,lon = 46.518839365687, 6.568393192707151

    message = (f"{lat},{lon}").encode("utf-8")
    client1_requests = ["library"]
    client2_requests = ["bar", "restaurant", "hotel"]
    client3_requests = ["cafe", "bar"]

    signature1 = measured(c1.sign_request, measurements["Client"]["sign_request"])(
        server_pk, credential1, message, client1_requests, measurements=measurements
    )
    signature2 = measured(c2.sign_request, measurements["Client"]["sign_request"])(
        server_pk, credential2, message, client2_requests, measurements=measurements
    )
    signature3 = measured(c3.sign_request, measurements["Client"]["sign_request"])(
        server_pk, credential3, message, client3_requests, measurements=measurements
    )

    assert signature1 is not None
    assert signature2 is not None
    assert signature3 is not None

    #The following three are valid signatures
    #So the response should be valid
    res1 = measured(s.check_request_signature, measurements["Server"]["check_request_signature"])(
        server_pk, message, client1_requests, signature1, measurements=measurements
    )

    res2 = measured(s.check_request_signature, measurements["Server"]["check_request_signature"])(
        server_pk, message, client2_requests, signature2, measurements=measurements
    )

    res3 = measured(s.check_request_signature, measurements["Server"]["check_request_signature"])(
        server_pk, message, client3_requests, signature3, measurements=measurements
    )

    assert res1
    assert res2
    assert res3
    return measurements


"""
A scenario where one client and one server are present.
We measure the metrics for one client and the server
"""
def eval_with_single_client():
    measurements = init_measurements()

    s = Server(measurement_mode=True)
    c1 = Client(measurement_mode=True)

    """
    Simulate a situation where 3 clients interact with the server
    """    
    server_subs = ["hotel", "library", "restaurant", "bar", "dojo", "cafe", "username"]

    #Client with valid subs
    client1_subs = ["library", "restaurant", "dojo"]
    client1_name = "can"

    server_sk,server_pk = measured(s.generate_ca, measurements["Server"]["generate_ca"])(server_subs, True, measurements=measurements)

    ######################################
    ##Prepare registration for all clients
    ######################################
    #Valid reg for c1

    issuance_req1, state1 = measured(c1.prepare_registration, measurements["Client"]["prepare_registration"])(server_pk, client1_name, client1_subs, measurements=measurements)
    assert issuance_req1 is not None
    
    ################################################
    ##Process registration by server for all clients
    ################################################
    registration_res1 = measured(s.process_registration, measurements["Server"]["process_registration"])(
        server_sk, server_pk, issuance_req1, client1_name, client1_subs, measurements=measurements
    )
    assert registration_res1 is not None

    ################################################
    ##Process registration response for all clients
    ################################################
    credential1 = measured(c1.process_registration_response, measurements["Client"]["process_registration_response"])(
        server_pk, registration_res1, state1, measurements=measurements
    )

    lat,lon = 46.518839365687, 6.568393192707151

    message = (f"{lat},{lon}").encode("utf-8")
    client1_requests = ["library", "dojo"]

    signature1 = measured(c1.sign_request, measurements["Client"]["sign_request"])(server_pk, credential1, message, client1_requests, measurements=measurements)

    assert signature1 is not None

    #The following is valid signature
    #So the response should be valid
    res1 = measured(s.check_request_signature, measurements["Server"]["check_request_signature"])(
        server_pk, message, client1_requests, signature1, measurements=measurements
    )

    assert res1
    return measurements


if __name__ == '__main__':
    print("Measurements running...")
    #Take command line argument
    num_exec = int(sys.argv[1]) #Number of executions
    
    #Check if the measurement folder already exists
    curr = os.getcwd()
    path = curr + "/measurements"
    dirExists = os.path.exists(path)

    #If the measuremtns folder does not exist, create it
    if not dirExists:
        os.makedirs(path)

    #Change working directory
    os.chdir(path)

    #Initialize the dictionary for the measurements
    measurements = init_measurements()
    measurements_temp = []

    #Run for num_exec times and record the results to the temporary array
    for _ in range(num_exec):
        measurements_temp.append(eval_with_three_clients())

    #Combine the results from multiple rows
    for measurement_temp in measurements_temp:
        for key1 in measurement_temp.keys():
            val1 = measurement_temp[key1]
            for key2 in val1.keys():
                m = measurement_temp[key1][key2]
                measurements[key1][key2].updateArray(m.delta_t, m.bytes_out)

    """Write each measurement on the corresponding file
    For example, the measurements for Client's sign_request function will be in
    "Client--sign_request.txt" file
    At the end of each file, we include the mean and standard error of the measurements
    """
    for key1 in measurements.keys():
            val1 = measurements[key1]
            for key2 in val1.keys():
                f = open(f"{key1}--{key2}.txt", "w")
                m = measurements[key1][key2]
                f.write("Time (ms) | Output Size (bytes):\n")
                f.write("-------------------------------\n")
                for i in range(len(m.delta_t)):
                    f.write(f"{str(round(m.delta_t[i], 3)): <18}")    
                    f.write(f"{m.bytes_out[i]}\n")        
                f.write("Average:\n")
                f.write(f"{str(round(stat.mean(m.delta_t), 3)): <18}")    
                f.write(f"{round(stat.mean(m.bytes_out), 3)}\n")   
                f.write("Std Error:\n")
                f.write(f"{round(stat.stdev(m.delta_t)/sqrt(len(m.delta_t)), 3): <18}")    
                f.write(f"{round(stat.stdev(m.bytes_out)/sqrt(len(m.bytes_out)), 3)}\n")           
                f.close()
    print("Measurements complete. You can now find the results in the measurements folder")
            
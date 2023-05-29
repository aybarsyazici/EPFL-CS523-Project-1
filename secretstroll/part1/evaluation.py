import test_registrationscheme
from measurement import Measurement, measured
from stroll import Client, Server

"""
A scenario where three clients and one server are present.
We measure the metrics for one client and the server
"""
def eval_with_three_clients():
    measurements = {}
    measurements["client"] = {"prepare_registration": Measurement(), "process_registration_response": Measurement(), "sign_request": Measurement()}
    measurements["server"] = {"generate_ca": Measurement(), "process_registration": Measurement(), "check_request_signature": Measurement()}
    measurements["issuance"] = {"sign_issue_request": Measurement(), "create_issue_request": Measurement()}
    measurements["signature"] = {"generate_key": Measurement()}

    s = Server(measurement_mode=True)
    c1 = Client(measurement_mode=True)
    c2 = Client()
    c3 = Client()

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
    client3_subs = ["bar", "dojo"]
    client3_name = "gustavo"

    server_sk,server_pk = measured(s.generate_ca, measurements["server"]["generate_ca"])(server_subs, True, measurements=measurements)

    ######################################
    ##Prepare registration for all clients
    ######################################
    #Valid reg for c1

    issuance_req1, state1 = measured(c1.prepare_registration, measurements["client"]["prepare_registration"])(server_pk, client1_name, client1_subs, measurements=measurements)
    assert issuance_req1 is not None

    #Valid reg for c2
    issuance_req2, state2 = c2.prepare_registration(
        server_pk, client2_name, client2_subs
    )
    assert issuance_req2 is not None

    #Valid reg for c3
    issuance_req3, state3 = c3.prepare_registration(
        server_pk, client3_name, client3_subs
    )
    assert issuance_req3 is not None
    
    ################################################
    ##Process registration by server for all clients
    ################################################
    registration_res1 = measured(s.process_registration, measurements["server"]["process_registration"])(
        server_sk, server_pk, issuance_req1, client1_name, client1_subs, measurements=measurements
    )
    assert registration_res1 is not None

    registration_res2 = measured(s.process_registration, measurements["server"]["process_registration"])(
        server_sk, server_pk, issuance_req2, client2_name, client2_subs, measurements=measurements
    )
    assert registration_res2 is not None

    registration_res3 = measured(s.process_registration, measurements["server"]["process_registration"])(
        server_sk, server_pk, issuance_req3, client3_name, client3_subs, measurements=measurements
    )
    assert registration_res3 is not None

    ################################################
    ##Process registration response for all clients
    ################################################
    credential1 = measured(c1.process_registration_response, measurements["client"]["process_registration_response"])(
        server_pk, registration_res1, state1
    )

    credential2 = c2.process_registration_response(
        server_pk, registration_res2, state2
    )

    credential3 = c3.process_registration_response(
        server_pk, registration_res3, state3
    )

    lat,lon = 46.518839365687, 6.568393192707151

    message = (f"{lat},{lon}").encode("utf-8")
    client1_requests = ["library"]
    client2_requests = ["bar", "dojo"]
    client3_requests = ["dojo", "bar"]

    signature1 = measured(c1.sign_request, measurements["client"]["sign_request"])(server_pk, credential1, message, client1_requests)
    signature2 = c2.sign_request(server_pk, credential2, message, client2_requests)
    signature3 = c3.sign_request(server_pk, credential3, message, client3_requests)

    assert signature1 is not None
    assert signature2 is not None
    assert signature3 is not None

    #The following three are valid signatures
    #So the response should be valid
    res1 = measured(s.check_request_signature, measurements["server"]["check_request_signature"])(
        server_pk, message, client1_requests, signature1, measurements=measurements
    )

    res2 = measured(s.check_request_signature, measurements["server"]["check_request_signature"])(
        server_pk, message, client2_requests, signature2, measurements=measurements
    )

    res3 = measured(s.check_request_signature, measurements["server"]["check_request_signature"])(
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
    measurements = {}
    measurements["Client"] = {"prepare_registration": Measurement(), "process_registration_response": Measurement(), "sign_request": Measurement()}
    measurements["Server"] = {"generate_ca": Measurement(), "process_registration": Measurement(), "check_request_signature": Measurement()}
    measurements["IssueScheme"] = {"sign_issue_request": Measurement(), "create_issue_request": Measurement()}
    measurements["SignatureScheme"] = {"generate_key": Measurement()}
    measurements["DisclosureProof"] = {"create_disclosure_proof": Measurement(), "verify_disclosure_proof": Measurement()}
    measurements["ProofHandler"] = {"generate": Measurement(), "verify": Measurement()}

    s = Server(measurement_mode=True)
    c1 = Client(measurement_mode=True)

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
        server_pk, registration_res1, state1
    )

    lat,lon = 46.518839365687, 6.568393192707151

    message = (f"{lat},{lon}").encode("utf-8")
    client1_requests = ["library"]

    signature1 = measured(c1.sign_request, measurements["Client"]["sign_request"])(server_pk, credential1, message, client1_requests, measurements=measurements)

    assert signature1 is not None

    #The following is valid signature
    #So the response should be valid
    res1 = measured(s.check_request_signature, measurements["Server"]["check_request_signature"])(
        server_pk, message, client1_requests, signature1, measurements=measurements
    )

    assert res1
    return measurements


measurements = eval_with_single_client()
for key1 in measurements.keys():
    val1 = measurements[key1]
    for key2 in val1.keys():
        val2 = measurements[key1][key2]
        print(key1, key2, val2.delta_t, val2.bytes_out)
from stroll import Server,Client
from credential import AnonymousCredential
from serialization import jsonpickle
from measurement import measured, Measurement
import time
import sys

def test_simpleregistration():
    """
    Simulate expected interaction between Server and Client
    """
    server_subs = ["hotel", "library", "restaurant", "bar", "dojo", "username"]
    server_sk,server_pk = Server.generate_ca(server_subs)
    server = Server()
    client = Client()
    client_subs = ["restaurant", "bar", "dojo"]
    client_name = "user123"
    
    # [CLIENT] Prepare registration
    issuance_req, state = client.prepare_registration(
        server_pk, client_name, client_subs
    )

    # [SERVER] Process registration
    registration_res = server.process_registration(
        server_sk, server_pk, issuance_req, client_name, client_subs
    )

    # [CLIENT] - Save credential 
    credential:bytes = client.process_registration_response(
        server_pk, registration_res, state
    )
    
    anonCred = jsonpickle.decode(credential)
    print("[CLIENT] AnonCred obtained: " + str(anonCred))
    # Now that the Client has obtainted his credential, he can sign requests with it
    # [CLIENT]  - Sign request with obtained credential
    lat,lon = 46.518839365687, 6.568393192707151
    message = (f"{lat},{lon}").encode("utf-8")
    types = ["restaurant", "bar"] #types of services to request
    # compute signature
    signature = client.sign_request(server_pk, credential, message, types)

    # [SERVER] - Check whether the signature is valid, or not  
    res = server.check_request_signature(
        server_pk, message, types, signature
    )
    assert res

def test_simple_failed_reg():
    """
    Simulate a situation where the proof provided by the user is wrong. 
    """
    server_subs = ["hotel", "library", "restaurant", "bar", "dojo", "username"]
    server_sk,server_pk = Server.generate_ca(server_subs)
    server = Server()
    client = Client()
    client_subs = ["restaurant", "bar", "dojo"]
    client_name = "user123"
    
    # [CLIENT] Prepare registration
    issuance_req, state = client.prepare_registration(
        server_pk, client_name, client_subs, True
    )

    # [SERVER] Process registration
    try:
        server.process_registration(
            server_sk, server_pk, issuance_req, client_name, client_subs
        )
    except:
        return
    
    assert False


def test_with_multiple_clients():
    s = Server()
    c1 = Client()
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

    server_sk,server_pk = s.generate_ca(server_subs)

    ######################################
    ##Prepare registration for all clients
    ######################################
    #Valid reg for c1
    issuance_req1, state1 = c1.prepare_registration(
        server_pk, client1_name, client1_subs
    )
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

    #Invalid reg for c3
    issuance_req_inv, _ = c1.prepare_registration(
        server_pk, client1_name, ["invalid_sub"]
    )
    assert issuance_req_inv is None
    
    ################################################
    ##Process registration by server for all clients
    ################################################
    registration_res1 = s.process_registration(
        server_sk, server_pk, issuance_req1, client1_name, client1_subs
    )
    assert registration_res1 is not None

    registration_res2 = s.process_registration(
        server_sk, server_pk, issuance_req2, client2_name, client2_subs
    )
    assert registration_res2 is not None

    registration_res3 = s.process_registration(
        server_sk, server_pk, issuance_req3, client3_name, client3_subs
    )
    assert registration_res3 is not None

    #Invalid subs, should return None
    registration_res_inv = s.process_registration(
        server_sk, server_pk, issuance_req3, client3_name, ["invalid_sub"]
    )
    assert registration_res_inv is None


    ################################################
    ##Process registration response for all clients
    ################################################
    credential1 = c1.process_registration_response(
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
    client3_invalid_requests = ["cafe"] #should be denied because the client is not subscribed to the cafe

    signature1 = c1.sign_request(server_pk, credential1, message, client1_requests)
    signature2 = c2.sign_request(server_pk, credential2, message, client2_requests)
    signature3 = c3.sign_request(server_pk, credential3, message, client3_requests)
    #signature_inv = c3.sign_request(server_pk, credential3, message, client3_invalid_requests)

    assert signature1 is not None
    assert signature2 is not None
    assert signature3 is not None
    #assert signature_inv is None

    #The following three are valid signatures
    #So the response should be valid
    res1 = s.check_request_signature(
        server_pk, message, client1_requests, signature1
    )

    res2 = s.check_request_signature(
        server_pk, message, client2_requests, signature2
    )

    res3 = s.check_request_signature(
        server_pk, message, client3_requests, signature3
    )

    assert res1
    assert res2
    assert res3

    #The following 2 are invalid requests
    #So the response will be null
    inv_res1 = s.check_request_signature(
        server_pk, message, ["bar", "dojo"], signature1
    )

    inv_res3 = s.check_request_signature(
        server_pk, message, ["hotel", "library"], signature3
    )

    assert inv_res1 is False
    assert inv_res3 is False
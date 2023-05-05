from stroll import Server,Client
from credential import AnonymousCredential
from serialization import jsonpickle

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
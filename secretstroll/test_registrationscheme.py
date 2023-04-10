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
    
    anonCred:AnonymousCredential = jsonpickle.decode(credential)
    print("Credentials obtained: " + str(anonCred.attributes))
    assert True

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


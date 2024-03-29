"""
Classes that you need to complete.
"""
from petrelic.multiplicative.pairing import G1
from typing import Any, Dict, List, Union, Tuple
from credential import (
    AnonymousCredential,
    BlindSignature, 
    PublicKey, 
    SecretKey, 
    SignatureScheme, 
    IssueScheme, 
    Attribute, 
    BlindSignature, 
    AttributeMap, 
    Signature,
    DisclosureProof,
    verify_disclosure_proof
    )
from petrelic.bn import Bn
# Optional import
from serialization import jsonpickle
import time
import sys
from measurement import measured


# Type aliases
State = tuple[Bn, AttributeMap]

class Server:
    """Server"""
    subscriptions: List[str] = None

    def __init__(self, measurement_mode=False):
        """
        Server constructor.
        """
        self.measurement_mode = measurement_mode
        return

    @staticmethod
    def generate_ca(
            subscriptions: List[str],
            measurement_mode = False,
            measurements = None
        ) -> Tuple[bytes, bytes]:
        """Initializes the credential system. Runs exactly once in the
        beginning. Decides on schemes public parameters and choses a secret key
        for the server.

        Args:
            subscriptions: a list of all valid attributes. Users cannot get a
                credential with a attribute which is not included here.

        Returns:
            tuple containing:
                - server's secret key
                - server's public information
            You are free to design this as you see fit, but the return types
            should be encoded as bytes.
        """
        appended_subscriptions = subscriptions + ["secret_key"]
        
        if measurement_mode:
            sk, pk = measured(SignatureScheme.generate_key, measurements["SignatureScheme"]["generate_key"])(appended_subscriptions)
        else:
            sk, pk = SignatureScheme.generate_key(appended_subscriptions)    

        return (jsonpickle.encode(sk).encode("utf-8"), jsonpickle.encode(pk).encode("utf-8"))

    def process_registration(
            self,
            server_sk: bytes,
            server_pk: bytes,
            issuance_request: bytes,
            username: str,
            subscriptions: List[str],
            measurements= None
        ) -> bytes:
        """ Registers a new account on the server.

        Args:
            server_sk: the server's secret key (serialized)
            issuance_request: The issuance request (serialized)
            username: username
            subscriptions: attributes


        Return:
            serialized response (the client should be able to build a
                credential with this response).
        """
        server_pk_parsed: PublicKey = jsonpickle.decode(server_pk)
        server_sk_parsed: SecretKey = jsonpickle.decode(server_sk)
        print(f"Subscriptions sent to the server are " + str(subscriptions))
        # Check if the subscriptions that are requested are valid
        if not set(subscriptions).issubset(set(server_pk_parsed.subscriptions.keys())):
            return None
            #raise ValueError("[SERVER] Invalid subscriptions")
        # We could check the users name and see if he has subscribed to the requested subscriptions
        # but we will not do that here
        issuer_attributes = {}
        for subscription in server_pk_parsed.subscriptions.keys():
            if subscription != "secret_key":
                if subscription in subscriptions:
                    issuer_attributes[subscription] = Bn(1)
                else:
                    issuer_attributes[subscription] = Bn(0)
        issuer_attributes["username"] = Bn.from_binary(username.encode("utf-8"))
        print(f"issuer_attributes are: " + str(issuer_attributes))

        if self.measurement_mode:
            blindSign = measured(IssueScheme.sign_issue_request, measurements["IssueScheme"]["sign_issue_request"])(server_sk_parsed, server_pk_parsed, jsonpickle.decode(issuance_request), issuer_attributes, measurements=measurements)
        else:
            blindSign = IssueScheme.sign_issue_request(server_sk_parsed, server_pk_parsed, jsonpickle.decode(issuance_request), issuer_attributes)

        print("[SERVER] Returning blind sign: " + str(blindSign))
        return jsonpickle.encode(blindSign)

    def check_request_signature(
        self,
        server_pk: bytes,
        message: bytes,
        revealed_attributes: List[str],
        signature: bytes,
        measurements= None
        ) -> bool:
        """ Verify the signature on the location request

        Args:
            server_pk: the server's public key (serialized)
            message: The message to sign
            revealed_attributes: revealed attributes
            signature: user's authorization (serialized)

        Returns:
            whether a signature is valid
        """
        server_pk = jsonpickle.decode(server_pk)

        proof: DisclosureProof = jsonpickle.decode(signature)
        disclosed_attributes = proof.revealed_attributes
        print("[SERVER] Disclosed attributes are: " + str(disclosed_attributes))
        for attr in revealed_attributes:
            print("[SERVER] Checking if " + str(attr) + " was disclosed")
            try:
                #print(attr,disclosed_attributes)
                #if one of the revealed attributes was not subscribed...invalidate signature
                if disclosed_attributes[attr] == 0:
                    return False  
            except:
                #the attr that the user wants to prove he has a valid subscription for, was not disclosed
                return False  

        if measurements is None:
            verified = verify_disclosure_proof(
                server_pk,proof,message
            )
        else:
            verified = measured(verify_disclosure_proof, measurements["DisclosureProof"]["verify_disclosure_proof"])(
                server_pk,proof,message, measurements=measurements
            )
        return verified


class Client:
    """Client"""

    def __init__(self, measurement_mode=False):
        """
        Client constructor.
        """
        self.secret = None
        self.measurement_mode = measurement_mode

    def prepare_registration(
            self,
            server_pk: bytes,
            username: str,
            subscriptions: List[str],
            testing: bool = False,
            measurements=False
        ) -> Tuple[bytes, State]:
        """Prepare a request to register a new account on the server.

        Args:
            server_pk: a server's public key (serialized)
            username: user's name
            subscriptions: user's subscriptions

        Return:
            A tuple containing:
                - an issuance request
                - A private state. You can use state to store and transfer information
                from prepare_registration to proceed_registration_response.
                You need to design the state yourself.
        """
        # Deserialize the server's public key
        server_pk: PublicKey = jsonpickle.decode(server_pk)
        # Check if the subscriptions are valid 
        if not set(subscriptions).issubset(set(server_pk.subscriptions)):
            return None, None
            #raise ValueError("[CLIENT] Invalid subscriptions")
        # create user attributes
        attributes = dict()
        # Subscriptions and username are server issued
        # User will only have one secret key
        self.secret = G1.order().random()

        attributes["secret_key"] = self.secret 
        # create issue req
        if self.measurement_mode:
            issue_req, private_state = measured(IssueScheme.create_issue_request, measurements["IssueScheme"]["create_issue_request"])(user_attributes=attributes, pk=server_pk, testing=testing, measurements=measurements)
        else:
            issue_req, private_state = IssueScheme.create_issue_request(user_attributes=attributes, pk=server_pk, testing=testing)
        return (jsonpickle.encode(issue_req), private_state)

    def process_registration_response(
            self,
            server_pk: bytes,
            server_response: bytes,
            private_state: State, 
            measurements=None
        ) -> bytes:
        """Process the response from the server.

        Args:
            server_pk a server's public key (serialized)
            server_response: the response from the server (serialized)
            private_state: state from the prepare_registration
            request corresponding to this response

        Return:
            credentials: create an attribute-based credential for the user
        """
        # Reconstruct server's response, which is a blind signature
        blindSign: BlindSignature = jsonpickle.decode(server_response)
        # Reconstruct the server's public key
        server_pk = jsonpickle.decode(server_pk)
        if measurements is None:
            credential = IssueScheme.obtain_credential(
                    pk=server_pk,
                    response=blindSign,
                    t = private_state
            )
        else:
            credential = measured(IssueScheme.obtain_credential, measurements["IssueScheme"]["obtain_credential"])(
                    pk=server_pk,
                    response=blindSign,
                    t = private_state
            )
        return jsonpickle.encode(credential).encode("utf-8")

    def sign_request(
            self,
            server_pk: bytes,
            credentials: bytes,
            message: bytes,
            types: List[str],
            measurements= None
        ) -> bytes:
        """Signs the request with the client's credential.

        Arg:
            server_pk: a server's public key (serialized)
            credential: client's credential (serialized)
            message: message to sign
            types: which attributes should be sent along with the request?

        Returns:
            A message's signature (serialized)
        """
        server_pk_parsed:PublicKey = jsonpickle.decode(server_pk)
        credential_parsed:AnonymousCredential = jsonpickle.decode(credentials)
        # Check if the types are valid
        if not set(types).issubset(set(credential_parsed.attributes.keys())):
            return None
            #raise ValueError("[CLIENT] Invalid types")
        # Check if the types are valid
        if not set(types).issubset(set(server_pk_parsed.subscriptions.keys())):
            return None
            #raise ValueError("[CLIENT] Invalid types")
        # Create the disclosure proof
        if measurements is None:    
            disclosure_proof = DisclosureProof.create_disclosure_proof(
                    credential_parsed,
                    types,
                    server_pk_parsed,
                    message
            )
        else: 
            disclosure_proof = measured(DisclosureProof.create_disclosure_proof, measurements["DisclosureProof"]["create_disclosure_proof"])(
                        credential_parsed,
                        types,
                        server_pk_parsed,
                        message,
                        measurements=measurements
                        )
        return jsonpickle.encode(disclosure_proof).encode("utf-8")


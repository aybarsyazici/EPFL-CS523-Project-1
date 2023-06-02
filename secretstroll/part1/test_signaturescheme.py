from credential import SignatureScheme, IssueScheme, DisclosureProof, verify_disclosure_proof
from petrelic.bn import Bn

def test_basic_message():
    """Test basic message"""
    message = ["Hello, world!".encode("utf-8")]
    sk, pk = SignatureScheme.generate_key(message)
    signature = SignatureScheme.sign(sk, message)
    assert SignatureScheme.verify(pk, signature, message)

def test_incorrect_basic_message():
    """Test incorrect basic message"""
    message = ["Hello, world!".encode("utf-8")]
    sk, pk = SignatureScheme.generate_key(message)
    signature = SignatureScheme.sign(sk, message)
    assert not SignatureScheme.verify(pk, signature, ["Hello, world".encode("utf-8")])

def test_multiple_messages():
    """Test multiple messages"""
    message = ["Hello, world!".encode("utf-8"), "Hello, world!".encode("utf-8"), "Merhaba, dünya!".encode("utf-8")]
    sk, pk = SignatureScheme.generate_key(message)
    signature = SignatureScheme.sign(sk, message)
    assert SignatureScheme.verify(pk, signature, message)

def test_incorrect_multiple_messages():
    """Test incorrect multiple messages"""
    message = ["Hello, world!".encode("utf-8"), "Hello, world!2".encode("utf-8")]
    sk, pk = SignatureScheme.generate_key(message)
    signature = SignatureScheme.sign(sk, message)
    assert not SignatureScheme.verify(pk, signature, ["Hello, world!".encode("utf-8"), "Merhaba, dünya!".encode("utf-8")])


def test_attribute_based_credentials_1():
    """"Test attribute based credentials"""
    sig = SignatureScheme()
    #Initialize user and issuer attributes
    issuer_attributes = {"issuer_attribute1": Bn(300), "issuer_attribute2": Bn(400), "issuer_attribute3": Bn(500)}
    user_attributes = {"user_attribute1": Bn(100), "user_attribute2": Bn(200)}
    # Create a List of strings using all attribute keys.
    all_attributes = list(issuer_attributes.keys()) + list(user_attributes.keys())
    sk, pk = sig.generate_key(all_attributes)
    # User creates issue request with their attributes
    issue_req, state = IssueScheme.create_issue_request(pk, user_attributes)
    # Issuer signs the user's request
    blinded_credential = IssueScheme.sign_issue_request(sk, pk, issue_req, issuer_attributes)
    # User obtains the credential
    credential = IssueScheme.obtain_credential(pk=pk, response=blinded_credential, t=state)
   
    #We will test one valid and one invalid message 
    valid_message = "This is a valid message.".encode()
    invalid_message = "An invalid message!".encode() 
    # At the prover. Hide the secret, which is part of the returned state.
    proof = DisclosureProof.create_disclosure_proof(pk=pk, credential=credential, revealed_attributes=["user_attribute1", "issuer_attribute1"], message=valid_message)
    # Valid message and proof should be verified
    assert verify_disclosure_proof(pk=pk, disclosure_proof=proof, message=valid_message)
    # An incorrect message should fail
    assert not verify_disclosure_proof(pk=pk, disclosure_proof=proof, message=invalid_message)
    # Incorrect proof should fail
    proof.random_sign.h = proof.random_sign.h ** 2
    assert not verify_disclosure_proof(pk=pk, disclosure_proof=proof, message=valid_message)    


def test_attribute_based_credentials_2():
    sig = SignatureScheme()
    #Initialize user and issuer attributes
    issuer_attributes = {"issuer_attribute1": Bn(300), "issuer_attribute2": Bn(400), "issuer_attribute3": Bn(500)}
    user_attributes = {"user_attribute1": Bn(100), "user_attribute2": Bn(200)}
    # Create a List of strings using all attribute keys.
    all_attributes = list(issuer_attributes.keys()) + list(user_attributes.keys())
    sk, pk = sig.generate_key(all_attributes)
    # User creates issue request with their attributes
    issue_req, state = IssueScheme.create_issue_request(pk, user_attributes)
    # Issuer signs the user's request
    blinded_credential = IssueScheme.sign_issue_request(sk, pk, issue_req, issuer_attributes)
    # User obtains the credential
    credential = IssueScheme.obtain_credential(pk=pk, response=blinded_credential, t=state)
   
    #We will test one valid and one invalid message 
    valid_message = "This is a valid message.".encode()
    invalid_message = "An invalid message!".encode() 
    # At the prover. Hide the secret, which is part of the returned state.
    proof = DisclosureProof.create_disclosure_proof(pk=pk, credential=credential, revealed_attributes=["user_attribute2"], message=valid_message)
    # Valid message and proof should be verified
    assert verify_disclosure_proof(pk=pk, disclosure_proof=proof, message=valid_message)
    # An incorrect message should fail
    assert not verify_disclosure_proof(pk=pk, disclosure_proof=proof, message=invalid_message)
    # Incorrect proof should fail
    proof.random_sign.h = proof.random_sign.h ** 2
    assert not verify_disclosure_proof(pk=pk, disclosure_proof=proof, message=valid_message)    
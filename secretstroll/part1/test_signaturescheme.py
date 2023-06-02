from credential import SignatureScheme, IssueScheme, DisclosureProof, verify_disclosure_proof
from petrelic.bn import Bn
from itertools import combinations


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


def test_ABC_selective_disclosure():
    """
    Test selective diclosure property of ABC
    The user reveals each possible combination of attributes to the issuer
    """
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

    #Get all combinations of attributes
    comb = []
    for i in range(len(all_attributes) + 1):
        comb_i = combinations(all_attributes, i)
        for c in comb_i:
            comb.append(c)

    #Test the ABC scheme for all possible permutations of the revealed attributes
    for revealed_comb in comb:
        #Reveal the corresponding combination of attributes
        proof = DisclosureProof.create_disclosure_proof(pk=pk, credential=credential, revealed_attributes=revealed_comb, message=valid_message)
        # Valid message and proof should be verified
        assert verify_disclosure_proof(pk=pk, disclosure_proof=proof, message=valid_message)
        # An incorrect message should fail
        assert not verify_disclosure_proof(pk=pk, disclosure_proof=proof, message=invalid_message)
        # Incorrect proof should fail
        proof.random_sign.h = proof.random_sign.h ** 2
        assert not verify_disclosure_proof(pk=pk, disclosure_proof=proof, message=valid_message)    


def test_ABC_verifier_unlinkability():
    """
    Test verifier unlinkability property of ABC
    We show that two instances of proofs obtained by the user (by revealing the same attributes)
    have different signatures and cannot be linked
    """
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

    # Create the first proof
    proof_1 = DisclosureProof.create_disclosure_proof(pk=pk, credential=credential, revealed_attributes=["user_attribute1", "user_attribute2"], message=valid_message)
    # Create the second proof
    proof_2 = DisclosureProof.create_disclosure_proof(pk=pk, credential=credential, revealed_attributes=["user_attribute1", "user_attribute2"], message=valid_message)

    #Test verifier unlinkability
    assert proof_1.random_sign != proof_2.random_sign

    #Now we show that both proofs are valid
    #Proof 1
    # Valid message and proof should be verified
    assert verify_disclosure_proof(pk=pk, disclosure_proof=proof_1, message=valid_message)
    # An incorrect message should fail
    assert not verify_disclosure_proof(pk=pk, disclosure_proof=proof_1, message=invalid_message)
    # Incorrect proof should fail
    proof_1.random_sign.h = proof_1.random_sign.h ** 2
    assert not verify_disclosure_proof(pk=pk, disclosure_proof=proof_1, message=valid_message) 

    #Proof 2
    # Valid message and proof should be verified
    assert verify_disclosure_proof(pk=pk, disclosure_proof=proof_2, message=valid_message)
    # An incorrect message should fail
    assert not verify_disclosure_proof(pk=pk, disclosure_proof=proof_2, message=invalid_message)
    # Incorrect proof should fail
    proof_2.random_sign.h = proof_2.random_sign.h ** 2
    assert not verify_disclosure_proof(pk=pk, disclosure_proof=proof_2, message=valid_message) 
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

def testABC():
    sig = SignatureScheme()
    # First, let's create the credential.
    issuer_attributes = {"issuer_attribute1": Bn(200), "issuer_attribute2": Bn(300), "issuer_attribute3": Bn(400)}
    user_attributes = {"user_attribute1": Bn(99), "user_attribute2": Bn(100)}
    # Create a List[str] of all attribute keys.
    all_attributes = list(issuer_attributes.keys()) + list(user_attributes.keys())
    sk, pk = sig.generate_key(all_attributes)
    # At the user.
    issue_req, state = IssueScheme.create_issue_request(pk, user_attributes)
    # At the issuer.
    blinded_credential = IssueScheme.sign_issue_request(sk, pk, issue_req, issuer_attributes)
    # At the user.
    credential = IssueScheme.obtain_credential(pk=pk, response=blinded_credential, t=state)
    # Now, let's test the credential against the verifier.
    msg = "lisbon".encode()
    # At the prover. Hide the secret, which is part of the returned state.
    proof = DisclosureProof.create_disclosure_proof(pk=pk, credential=credential, revealed_attributes=["user_attribute1", "issuer_attribute1"], message=msg)
    # At the verifier.
    assert verify_disclosure_proof(pk=pk, disclosure_proof=proof, message=msg)
    # Test incorrect message.
    assert not verify_disclosure_proof(pk=pk, disclosure_proof=proof, message="zurich".encode())
    # Test incorrect proof.
    proof.random_sign.h = proof.random_sign.h ** 2
    assert not verify_disclosure_proof(pk=pk, disclosure_proof=proof, message=msg)
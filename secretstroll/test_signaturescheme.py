from credential import SignatureScheme

def test_basic_message():
    """Test basic message"""
    message = ["Hello, world!".encode("utf-8")]
    sk, pk = SignatureScheme.generate_key(1)
    signature = SignatureScheme.sign(sk, message)
    assert SignatureScheme.verify(pk, signature, message)

def test_incorrect_basic_message():
    """Test incorrect basic message"""
    message = ["Hello, world!".encode("utf-8")]
    sk, pk = SignatureScheme.generate_key(1)
    signature = SignatureScheme.sign(sk, message)
    assert not SignatureScheme.verify(pk, signature, ["Hello, world".encode("utf-8")])

def test_multiple_messages():
    """Test multiple messages"""
    message = ["Hello, world!".encode("utf-8"), "Hello, world!".encode("utf-8"), "Merhaba, dünya!".encode("utf-8")]
    sk, pk = SignatureScheme.generate_key(len(message))
    signature = SignatureScheme.sign(sk, message)
    assert SignatureScheme.verify(pk, signature, message)

def test_incorrect_multiple_messages():
    """Test incorrect multiple messages"""
    message = ["Hello, world!".encode("utf-8"), "Hello, world!2".encode("utf-8")]
    sk, pk = SignatureScheme.generate_key(len(message))
    signature = SignatureScheme.sign(sk, message)
    assert not SignatureScheme.verify(pk, signature, ["Hello, world!".encode("utf-8"), "Merhaba, dünya!".encode("utf-8")])
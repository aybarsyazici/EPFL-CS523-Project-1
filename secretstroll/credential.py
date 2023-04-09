"""
Skeleton credential module for implementing PS credentials

The goal of this skeleton is to help you implementing PS credentials. Following
this API is not mandatory and you can change it as you see fit. This skeleton
only provides major functionality that you will need.

You will likely have to define more functions and/or classes. In particular, to
maintain clean code, we recommend to use classes for things that you want to
send between parties. You can then use `jsonpickle` serialization to convert
these classes to byte arrays (as expected by the other classes) and back again.

We also avoided the use of classes in this template so that the code more closely
resembles the original scheme definition. However, you are free to restructure
the functions provided to resemble a more object-oriented interface.
"""

from math import prod
from typing import Any, List, Tuple, Dict

from serialization import jsonpickle
from petrelic.multiplicative.pairing import G1, G2, G1Element, G2Element, GTElement
from petrelic.bn import Bn

# Type hint aliases
# Feel free to change them as you see fit.
# Maybe at the end, you will not need aliases at all!
class PublicKey:
    def __init__(self, g: G1Element, Y: List[G1Element], gh: G2Element, Xh: G2Element, Yh: List[G2Element]):
        self.g = g
        self.gh = gh
        self.Xh = Xh
        self.Y = Y
        self.Yh = Yh

class SecretKey:
    def __init__(self, x: int, X: G1Element, y: List[int]):
        self.x = x
        self.X = X
        self.y = y

class Signature:
    def __init__(self, h: G1Element, H: G1Element):
        self.h = h
        self.H = H
Attribute = Any
AttributeMap = Any
IssueRequest = Any
BlindSignature = Any
AnonymousCredential = Any
DisclosureProof = Any


######################
## SIGNATURE SCHEME ##
######################
# Returns a random integer from Z_p, i.e., in [0, p-1].
def random_Zp() -> Bn:
    import random
    # Acquire the prime order p.
    p = G1.order().random()
    return p

# Class implementing the PS signature scheme.
class SignatureScheme:
    @staticmethod
    def generate_key(
            attribute_len: int
        ) -> Tuple[SecretKey, PublicKey]:
        """ Generate signer key pair """
        # Generators
        g: G1Element = G1.generator() ** random_Zp()
        gh: G2Element = G2.generator() ** random_Zp()
        # private keys
        x = random_Zp()
        X: G1Element = g ** x
        y = [random_Zp() for _ in range(attribute_len)]
        # public keys
        Xh: G2Element = gh ** x
        Y: List[G1Element] = [g ** y_i for y_i in y]
        Yh: List[G2Element] = [gh ** y_i for y_i in y]
        return (SecretKey(x, X, y), PublicKey(g, Y, gh, Xh, Yh))
    
    @staticmethod
    def sign(
            sk: SecretKey,
            msgs: List[bytes]
        ) -> Signature:
        """ Sign a vector of messages """
        # Firstly, the msg length should be the same as the attribute length
        # i.e., the length of sk.y
        assert len(msgs) == len(sk.y)
        # We need to convert the messages into integers
        int_msgs = [Bn.from_binary(msg) for msg in msgs]
        # Now pick a random h
        h = G1.generator() ** random_Zp()
        # The returned signature will beo of the form (h, H)
        # where H = h^(x + sum(y_i * m_i))
        exponent = sk.x + sum([sk.y[i] * int_msgs[i] for i in range(len(sk.y))])
        H = h ** exponent
        return Signature(h, H)
    
    @staticmethod
    def verify(
            pk: PublicKey,
            signature: Signature,
            msgs: List[bytes]
        ) -> bool:
        """ Verify the signature on a vector of messages """
        # Firstly, make sure that the first element is not the identity
        if signature.h == G1.neutral_element():
            return False
        # Secondly, the msg length should be the same as the attribute length
        # i.e., the length of pk.Yh
        assert len(msgs) == len(pk.Yh)
        # We need to convert the messages into integers
        int_msgs = [Bn.from_binary(msg) for msg in msgs]
        # Now we need to compute the left hand side of the equation
        # i.e., e(h, Xh) * prod(e(Yh_i, g^m_i))
        lhs = signature.h.pair(pk.Xh)
        for i in range(len(pk.Yh)):
            lhs *= signature.h.pair(pk.Yh[i]** int_msgs[i])
        # Now we need to compute the right hand side of the equation
        # i.e., e(H, gh)
        rhs = signature.H.pair(pk.gh)
        # Finally, we can check if the two sides are equal
        return lhs == rhs


#################################
## ATTRIBUTE-BASED CREDENTIALS ##
#################################

## ISSUANCE PROTOCOL ##

def create_issue_request(
        pk: PublicKey,
        user_attributes: AttributeMap
    ) -> IssueRequest:
    """ Create an issuance request

    This corresponds to the "user commitment" step in the issuance protocol.

    *Warning:* You may need to pass state to the `obtain_credential` function.
    """
    raise NotImplementedError()


def sign_issue_request(
        sk: SecretKey,
        pk: PublicKey,
        request: IssueRequest,
        issuer_attributes: AttributeMap
    ) -> BlindSignature:
    """ Create a signature corresponding to the user's request

    This corresponds to the "Issuer signing" step in the issuance protocol.
    """
    raise NotImplementedError()


def obtain_credential(
        pk: PublicKey,
        response: BlindSignature
    ) -> AnonymousCredential:
    """ Derive a credential from the issuer's response

    This corresponds to the "Unblinding signature" step.
    """
    raise NotImplementedError()


## SHOWING PROTOCOL ##

def create_disclosure_proof(
        pk: PublicKey,
        credential: AnonymousCredential,
        hidden_attributes: List[Attribute],
        message: bytes
    ) -> DisclosureProof:
    """ Create a disclosure proof """
    raise NotImplementedError()


def verify_disclosure_proof(
        pk: PublicKey,
        disclosure_proof: DisclosureProof,
        message: bytes
    ) -> bool:
    """ Verify the disclosure proof

    Hint: The verifier may also want to retrieve the disclosed attributes
    """
    raise NotImplementedError()

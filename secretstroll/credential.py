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
from proof_handler import ProofHandler, PedersenProof
Attribute = Bn
AttributeMap = Dict[str, Attribute]

DisclosureProof = Any
# Type hint aliases
# Feel free to change them as you see fit.
# Maybe at the end, you will not need aliases at all!
class PublicKey:
    subscriptions: Dict[str, int] = None # This is a dictionary that maps a subscription to its index in the list of subscriptions
    def __init__(self, g: G1Element, Y: List[G1Element], gh: G2Element, Xh: G2Element, Yh: List[G2Element], subscriptions: List[str]):
        self.g = g
        self.gh = gh
        self.Xh = Xh
        self.Y = Y
        self.Yh = Yh
        self.subscriptions = {subscription: i for i, subscription in enumerate(subscriptions)}
        print("Subscritpions: ", self.subscriptions)

    # Override str method
    def __str__(self):
        return f"g:{self.g}, gh:{self.gh}, Xh:{self.Xh}, Y:{self.Y}, Yh:{self.Yh}, subscriptions: " + str(self.subscriptions)

class SecretKey:
    def __init__(self, x: int, X: G1Element, y: List[int]):
        self.x = x
        self.X = X
        self.y = y

class Signature:
    def __init__(self, h: G1Element, H: G1Element):
        self.h = h
        self.H = H
    def __str__(self):
        return f"Signature | h: {self.h}, H: {self.H}"

class BlindSignature:
    def __init__(self, sign: Signature, attributes: AttributeMap):
        self.sign = sign
        self.attributes = attributes
    def __str__(self):
        return f"BlindSignature | {self.sign}, attributes: " + str(self.attributes)

class AnonymousCredential:
    def __init__(self, sign: Signature, attributes: AttributeMap):
        self.sign = sign
        self.attributes = attributes

######################
## SIGNATURE SCHEME ##
######################

# Class implementing the PS signature scheme.
class SignatureScheme:
    @staticmethod
    def generate_key(
            attributes: List[str]
        ) -> Tuple[SecretKey, PublicKey]:
        """ Generate signer key pair """
        # Generators
        g: G1Element = G1.generator() ** G1.order().random()
        gh: G2Element = G2.generator() ** G1.order().random()
        # private keys
        x = G1.order().random()
        X: G1Element = g ** x
        y = [G1.order().random() for _ in range(len(attributes))]
        # public keys
        Xh: G2Element = gh ** x
        Y: List[G1Element] = [g ** y_i for y_i in y]
        Yh: List[G2Element] = [gh ** y_i for y_i in y]
        return (SecretKey(x, X, y), PublicKey(g, Y, gh, Xh, Yh,attributes))
    
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
        h = G1.generator() ** G1.order().random()
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
        # i.e., e(h, Xh * prod(Yh[i]^m_i)) 
        lhs = signature.h.pair(pk.Xh)
        for i in range(len(pk.Yh)):
            lhs *= signature.h.pair(pk.Yh[i] ** int_msgs[i])
        # Now we need to compute the right hand side of the equation
        # i.e., e(H, gh)
        rhs = signature.H.pair(pk.gh)
        # Finally, we can check if the two sides are equal
        return lhs == rhs


#################################
## ATTRIBUTE-BASED CREDENTIALS ##
#################################

## ISSUANCE PROTOCOL ##

class IssueRequest:
    def __init__(self, c: G1Element, p_proof: PedersenProof):
        self.c = c
        self.proof = p_proof

class IssueScheme:
    @staticmethod
    def create_issue_request(
            pk: PublicKey,
            user_attributes: AttributeMap,
            testing: bool = False
        ) -> Tuple[IssueRequest, Bn]:
        """ Create an issuance request

        This corresponds to the "user commitment" step in the issuance protocol.
        """
        # User will calculate a commitment
        # c = g^t * prod(Y[i]^m[i])
        # where t is a random integer
        # and m[i] is the attribute value
        # and Y[i] is the public key for the attribute
        t = G1.order().random()
        c = pk.g ** t
        for attribute_name, attribute_value in user_attributes.items():
            i = pk.subscriptions[attribute_name]
            c *= pk.Y[i] ** attribute_value
        # User will also create a proof using the ProofHandler
        # get the public values necessary
        pk_y_vals = []
        secret_user_vals = []
        for attr in user_attributes:
            i = pk.subscriptions[attr]
            pk_y_vals.append(pk.Y[i])
            secret_user_vals.append(user_attributes[attr])
        if testing: # if testing is set the true, we generate a wrong proof on purpose 
            proof = ProofHandler.generate_wrong(
                    to_prove = c,
                    secret_values = [t] + secret_user_vals,
                    public_values=[pk.g] + pk_y_vals,
                    )
            return IssueRequest(c, proof), t
        else:
            proof = ProofHandler.generate(
                to_prove=c,
                public_values=[pk.g] + pk_y_vals,
                secret_values=[t] + secret_user_vals 
            )
            return IssueRequest(c, proof), t

    @staticmethod
    def sign_issue_request(
            sk: SecretKey,
            pk: PublicKey,
            request: IssueRequest,
            issuer_attributes: AttributeMap
        ) -> Signature:
        """ Create a signature corresponding to the user's request

        This corresponds to the "Issuer signing" step in the issuance protocol.
        """
        assert len(issuer_attributes) <= len(sk.y)
        if not ProofHandler.verify(
            to_prove=request.c,
            proof=request.proof
            ):
            raise Exception("Incorrect proof!")
        # Issuer will do a blind signature
        # It will add his attributes to the user's attributes
        # and then sign the result
        # h = g^u where u is a random integer
        # H = (sk.X*request.c*prod(pk.Y[i]^issuer_attributes[i]))^u
        u = G1.order().random()
        h = pk.g ** u
        H = (sk.X * request.c)
        for attribute_name, attribute_value in issuer_attributes.items():
            i = pk.subscriptions[attribute_name]
            Y = pk.Y[i]
            H *= Y**attribute_value
        H = H**u
        return Signature(h, H)

    @staticmethod
    def obtain_credential(
            pk: PublicKey,
            t: Bn,
            response: Signature
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

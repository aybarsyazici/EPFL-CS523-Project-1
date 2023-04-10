from petrelic.multiplicative.pairing import  G1Element, G1
from typing import List
from functools import reduce
from petrelic.bn import Bn
import hashlib

class PedersenProof:
    def __init__(self, challenge: int, response: List[int], public_values: List[int]):
        self.challenge = challenge
        self.response = response
        self.public_values = public_values


def calc_challenge(
        to_prove: G1Element,
        commitment: G1Element,
        public_values: List[G1Element],
    ) -> int:
    """ Compute the challenge
    """
    # challenge = Hash of (to_prove, commitment, public_values[0], ..., public_values[n])
    challenge = reduce(lambda x, y: "{}{}".format(x,y), 
                        [to_prove.to_binary(), commitment.to_binary()] +
                            [x.to_binary() for x in public_values])
    return Bn.from_binary(hashlib.sha256(challenge.encode()).digest())

class ProofHandler:
    # This class handles the zero knowledge proof of a Pedersen commitment
    # We use the Schnorr protocol
    @staticmethod
    def generate(
            to_prove: G1Element,
            secret_values: List[int],
            public_values: List[int],
        ) -> PedersenProof:
        """ Prove that the commitment is a valid Pedersen commitment
        """
        assert(len(secret_values) == len(public_values))
        # For each secret value, we need to generate a random value
        rands = [G1.order().random() for _ in secret_values]
        # Knowing the random values, we can compute the commitment
        # commitment = public_values[0] ** secret_values[0] * ... * public_values[n] ** secret_values[n]
        commitment = G1.neutral_element()
        for i in range(len(secret_values)):
            commitment *= public_values[i] ** rands[i]
        # We need to compute the challenge
        challenge = calc_challenge(to_prove, commitment, public_values)
        # We can now compute the response
        # response = rands[0] + challenge * secret_values[0], ..., rands[n] + challenge * secret_values[n]
        response = [rands[i] + challenge * secret_values[i] for i in range(len(secret_values))]
        print("[PROOF GENERATE]: Sending Response: " + str(response))
        print("[PROOF GENERATE]: Public vals are: " + str(public_values))
        return PedersenProof(challenge=challenge, response=response, public_values=public_values)
    

    @staticmethod
    def verify(
            to_prove: G1Element,
            proof: PedersenProof
        ) -> bool:
        """ Verify that the commitment is a valid Pedersen commitment
        """
        public_values = proof.public_values
        print("[PROOF VERIFY]: Public vals used are: " + str(public_values))
        print("[PROOF VERIFY]: Sent Responses are " + str(proof.response))
        assert(len(proof.response) == len(public_values))
        # Compute the commitment
        commitment_prime = G1.neutral_element()
        for i in range(len(proof.response)):
            commitment_prime *= public_values[i] ** proof.response[i]
        # Compute the challenge
        commitment_prime *= to_prove ** (-1*proof.challenge)
        challenge_prime = calc_challenge(to_prove, commitment_prime, public_values)
        # Check that the challenge is the same
        return challenge_prime == proof.challenge


"""
Secret sharing scheme.
"""

from __future__ import annotations
import random

from typing import List

from expression import Scalar


# NOTE: Keep this large enough to pass the tests.
default_q = 520633 #10337


def rand_Zq(q=default_q):
    """Returns a random element from Z_q."""
    return random.randint(0, q - 1)

class Share:
    """
    A secret share in a finite field.
    """

    def __init__(self, index, value):
        self.index = index
        self.value = value

    def __repr__(self):
        # Helps with debugging.
        return f"Share({self.index}, {self.value})"

    def __add__(self, other):
        if isinstance(other, Scalar):
            if self.index == 0:
                return Share(0, self.value + other.value)
            return Share(self.index, self.value)    
        #else, both elements are shares
        return Share(self.index, self.value + other.value)     
    
    
    def __sub__(self, other):
        raise NotImplementedError("You need to implement this method.")

    def __mul__(self, other):
        raise NotImplementedError("You need to implement this method.")

    def serialize(self):
        """Convert object to a serialized representation."""
        s = f"{self.index}|{self.value}"
        return s.encode("utf-8")


    @staticmethod
    def deserialize(serialized) -> Share:
        """Restore object from its serialized representation."""
        index, value = serialized.split(b"|")
        return Share(int(index), int(value))


def gen_share(secret: int, num_shares: int) -> List[Share]:
    """ Given a secret and the number of participants in the SMC protocol,
    generate the secret shares.
    """
    # Calculate s_i for i \in [1, N-1]
    share_values = [rand_Zq() for _ in range(num_shares - 1)]
    # Calculate s_0 and prepend.
    share_values = [(secret - sum(share_values)) % default_q] + share_values
    # Return the shares s_0, s_1, ..., s_{N-1}
    return [Share(i, s) for i, s in enumerate(share_values)]
    


def reconstruct_secret(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    return sum([s.value for s in shares]) % default_q

def send_share(share: Share, receiver_id: str, secret_id: int, comm: Communication) -> None:
    secret_id_int = int.from_bytes(secret_id, byteorder="big")
    label = f"{secret_id_int}"
    print(f"SMCParty: Sending secret share {label}: {comm.client_id} -> {receiver_id}")
    comm.send_private_message(receiver_id, label, share.serialize())

def retrieve_share(id: int, comm: Communication) -> Share:
    """Retrieve a share from the server."""
    secret_id_int = int.from_bytes(id, byteorder="big")
    print(f"SMCParty: Retrieving secret share {secret_id_int}: {comm.client_id}")
    share = Share.deserialize(comm.retrieve_private_message(secret_id_int))
    print(f"SMCParty: Retrieved secret share {secret_id_int}: {comm.client_id} -> {share}")
    return share



# Feel free to add as many methods as you want.

"""
Secret sharing scheme.
"""

from __future__ import annotations
import random
import sys

import base64
from typing import List, Optional

from expression import Scalar
ID_BYTES = 4

def gen_id() -> bytes:
    id_bytes = bytearray(
        random.getrandbits(8) for _ in range(ID_BYTES)
    )
    return base64.b64encode(id_bytes)


# NOTE: Keep this large enough to pass the tests.
default_q = 520633 


def rand_Zq(q=default_q):
    """Returns a random element from Z_q."""
    return random.randint(0, q - 1)

class Share:
    """
    A secret share in a finite field.
    """

    def __init__(self, index, value, id: Optional[bytes] = None, beaver_triplets: Optional[List[Share]] = None):
        self.index = index
        self.value = value % default_q
        if id is None:
            id = gen_id()
        self.id = id
        self.beaver_triplets = beaver_triplets
        self.d:int = None
        self.e:int = None

    def __repr__(self):
        # Helps with debugging.
        return f"Share({self.id}, {self.index}, {self.value})"

    def __add__(self, other):
        if isinstance(other, int):
            if self.index == 0:
                return Share(0, self.value + other)
            return Share(self.index, self.value)    
        #else, both elements are shares
        return Share(self.index, self.value + other.value)     
    
    def __sub__(self, other):
        if isinstance(other, int):
            if self.index == 0:
                return Share(0, self.value - other)
            return Share(self.index, self.value)    
        #else, both elements are shares
        return Share(self.index, self.value - other.value)
    
    def __mul__(self, other):
        if isinstance(other, int):
            return Share(self.index, self.value * other)
        else:
            if(self.d is None): raise ValueError("d is not set, should NEVER happen")
            if(self.e is None): raise ValueError("e is not set, should NEVER happen")
            # Locally compute share of [sv] = de + d[b] + e[a] + [c]
            a_share = self.beaver_triplets[0]
            b_share = self.beaver_triplets[1]
            c_share = self.beaver_triplets[2]
            new_value = (c_share + self.d*self.e + b_share*self.d + a_share*self.e)
            return Share(self.index, new_value.value)

    # Override reverse add
    def __radd__(self, other):
        if(not isinstance(other, int)): raise ValueError("Should not happen")
        return self.__add__(other)
    
    # Override reverse sub
    def __rsub__(self, other):
        if(not isinstance(other, int)): raise ValueError("Should not happen")
        if self.index == 0:
            return Share(0, other - self.value)
        return Share(self.index, 0-self.value)   

    # Override reverse mul
    def __rmul__(self, other):
        if(not isinstance(other, int)): raise ValueError("Should not happen")
        return self.__mul__(other) 

    def serialize(self):
        """Convert object to a serialized representation."""
        s = f"{self.index}|{self.value}|{self.id}"
        return s
    
    def serialize_bytes(self):
        """Convert object to a serialized representation."""
        s = f"{self.index}|{self.value}|{self.id}"
        return s.encode('utf-8')

    @staticmethod
    def deserialize(serialized) -> Share:
        """Restore object from its serialized representation."""
        index, value, id = serialized.split("|")
        return Share(int(index), int(value), id=id)

    @staticmethod
    def deserialize_bytes(serialized) -> Share:
        """Restore object from its serialized representation."""
        index, value, id = serialized.split(b"|")
        return Share(int(index), int(value), id=id.decode('utf-8'))



def gen_share(secret: int, num_shares: int, secret_id: Optional[bytes] = None) -> List[Share]:
    """ Given a secret and the number of participants in the SMC protocol,
    generate the secret shares.
    """
    # Calculate s_i for i \in [1, N-1]
    share_values = [rand_Zq() for _ in range(num_shares - 1)]
    # Calculate s_0 and prepend.
    share_values = [(secret - sum(share_values)) % default_q] + share_values
    # Return the shares s_0, s_1, ..., s_{N-1}
    if secret_id is not None:
        return [Share(i, s, id=secret_id) for i, s in enumerate(share_values)]
    return [Share(i, s) for i, s in enumerate(share_values)]
    

def reconstruct_shares(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    print("TO RECONSTRUCT: ", shares)
    return sum([s.value for s in shares]) % default_q

#sends serialized message and returns the length of the serialized message
def send_share(share: Share, receiver_id: str, secret_id: bytes, comm: Communication) -> None:
    secret_id_int = int.from_bytes(secret_id, byteorder="big")
    label = f"{secret_id_int}"
    print(f"SMCParty: Sending secret share {label}: {comm.client_id} -> {receiver_id}")
    serialized = share.serialize_bytes()
    comm.send_private_message(receiver_id, label, serialized)
    return sys.getsizeof(serialized)

def retrieve_share(id: bytes, comm: Communication) -> Share:
    """Retrieve a share from the server."""
    secret_id_int = int.from_bytes(id, byteorder="big")
    label = f"{secret_id_int}"
    print(f"SMCParty: Retrieving secret share {label}: {comm.client_id}")
    retrieved = comm.retrieve_private_message(label)
    share = Share.deserialize_bytes(retrieved)
    print(f"SMCParty: Retrieved secret share {label}: {comm.client_id} -> {share}")
    return share, sys.getsizeof(retrieved)

def publish_result(share: Share, comm: Communication):
    """Publicly announce the final result"""
    label = f"{comm.client_id}"
    print(f"SMCParty: Broadcasting result share {label}: {comm.client_id} ->")
    serialized = Share.serialize_bytes(share)
    comm.publish_message(label, serialized)
    return sys.getsizeof(serialized)

def receive_public_results(comm: Communication, participant_ids: list):
    public_shares = []
    total_bytes = 0
    for participant in participant_ids:
        label = f"{participant}"
        print(f"SMCParty: Receiving result share {label}: -> {comm.client_id}")
        payload = comm.retrieve_public_message(participant, label)
        total_bytes += sys.getsizeof(payload)
        public_shares.append(Share.deserialize_bytes(payload))
    return public_shares, total_bytes

def get_beaver_triplet(comm: Communication, secret_id: int):
    """Get a beaver triplet from the server."""
    triplets = comm.retrieve_beaver_triplet_shares(str(secret_id))
    print("GOT TRIPLETS: " + str(triplets) + " FOR SECRET ID: " + str(secret_id))
    return triplets

def publish_triplet(share: Share, comm: Communication, d_or_e: str, secret_id: int):
    """Publish computed triplet share"""
    label = f"{comm.client_id}-{d_or_e}-{str(secret_id)}"
    print(f"SMCParty: Broadcasting triplet share {label}: {comm.client_id} -> {share}")
    serialized = Share.serialize_bytes(share)
    comm.publish_message(label, serialized)
    return sys.getsizeof(serialized)

def get_all_triplets(comm: Communication, participant_ids: list, secret_id: int) -> tuple(int,int):
    # First get all d values
    d = None
    e = None
    total_bytes = 0
    for participant in participant_ids:
        print(f"SMCParty: {comm.client_id}: Trying to receive d/e index: {str(secret_id)} from {participant}")
        label = f"{participant}-d-{str(secret_id)}"
        #print(f"SMCParty: Receiving triplet share {label}: -> {comm.client_id}")
        payload = comm.retrieve_public_message(sender_id=participant, label=label)
        print(f"SMCParty: {comm.client_id}: Received d{str(secret_id)} from {participant}: -> {Share.deserialize_bytes(payload)}")
        if d is None:
            d = Share.deserialize_bytes(payload).value
        else:
            d += Share.deserialize_bytes(payload).value
        label = f"{participant}-e-{secret_id}" 
        payload = comm.retrieve_public_message(sender_id=participant, label=label)
        print(f"SMCParty: {comm.client_id}: Received e{str(secret_id)} from {participant}: -> {Share.deserialize_bytes(payload)}")
        total_bytes += sys.getsizeof(payload)
        if e is None:
            e = Share.deserialize_bytes(payload).value 
        else:
            e += Share.deserialize_bytes(payload).value
        d = d % default_q
        e = e % default_q
    print(f"SMCParty: {comm.client_id} Finished getting d/e index: {str(secret_id)}")
    return d, e, total_bytes

# For use case
def publish_result_for_class(share: Share, comm: Communication, lecture: str, type: str):
    """Publicly announce the final result"""
    label = f"{comm.client_id}|{lecture}|{type}"
    print(f"SMCParty: Broadcasting result share {label}: {comm.client_id} ->")
    serialized = Share.serialize_bytes(share)
    comm.publish_message(label, serialized)

def receive_public_results_for_class(comm: Communication, participant_ids: list, lecture: str, type: str):
    public_shares = []
    for participant in participant_ids:
        label = f"{participant}|{lecture}|{type}"
        print(f"SMCParty: Receiving result share {label}: -> {comm.client_id}")
        payload = comm.retrieve_public_message(participant, label)
        public_shares.append(Share.deserialize_bytes(payload))
    return public_shares

# Feel free to add as many methods as you want.

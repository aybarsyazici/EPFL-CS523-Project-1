"""
Trusted parameters generator.

MODIFY THIS FILE.
"""

import collections
from typing import (
    Dict,
    Set,
    Tuple,
)

from communication import Communication
from secret_sharing import(
    gen_share,
    Share,
)
import random


# Feel free to add as many imports as you want.


class TrustedParamGenerator:
    """
    A trusted third party that generates random values for the Beaver triplet multiplication scheme.
    """

    def __init__(self):
        self.participant_ids: Set[str] = set()
        self.a = -1
        self.b = -1
        self.c = -1
        self.triplets = {}
        self.tripletIndeces = {}

    def add_participant(self, participant_id: str) -> None:
        """
        Add a participant.
        """
        self.participant_ids.add(participant_id)

    def retrieve_share(self, client_id: str, op_id: str) -> Tuple[Share, Share, Share]:
        """
        Retrieve a triplet of shares for a given client_id.
        """
        if client_id not in self.participant_ids:
            raise ValueError("Client not registered")
        if op_id not in self.triplets:
            self.generate_new_triplet(op_id)
        currentIndex = self.tripletIndeces[op_id]
        toReturn = (self.triplets[op_id][0][currentIndex], self.triplets[op_id][1][currentIndex], self.triplets[op_id][2][currentIndex])
        self.tripletIndeces[op_id] += 1
        return toReturn

    def generate_new_triplet(self, secret_id: str) -> None:
        self.a = random.randint(0,520633-1) #default_q
        self.b = random.randint(0,520633-1) #default_q
        self.c = (self.a * self.b) % 520633 #default_q
        print(f"Generated new triplet: {self.a}, {self.b}, {self.c} for {secret_id}")
        shares = []
        for secret in [self.a,self.b,self.c]:
            shares.append(gen_share(secret, len(self.participant_ids)))
        self.triplets[secret_id] = shares
        self.tripletIndeces[secret_id] = 0
        

    # Feel free to add as many methods as you want.

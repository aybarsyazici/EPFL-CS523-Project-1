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


    def add_participant(self, participant_id: str) -> None:
        """
        Add a participant.
        """
        self.participant_ids.add(participant_id)

    def retrieve_share(self, client_id: str, op_id: str) -> Tuple[Share, Share, Share]:
        """
        Retrieve a triplet of shares for a given client_id.
        """
        raise NotImplementedError("You need to implement this method.")

    def generate_new_triplet(self):
        self.a = random.randint(0,1000000)
        self.b = random.randint(0,1000000)
        self.c = self.a * self.b

    # Feel free to add as many methods as you want.

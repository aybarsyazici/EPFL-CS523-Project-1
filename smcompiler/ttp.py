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
        print(f"TTP: Generated new triplet shares: {shares} for {secret_id}")
        self.tripletIndeces[secret_id] = 0
        

# a: [Share(b'5cWs8g==', 0, 377149), Share(b'ISLUmg==', 1, 200216), Share(b'6jH88g==', 2, 345401)], 
# b: [Share(b'GTPKrw==', 0, 465161), Share(b'x8/YTw==', 1, 336692), Share(b'9B1cQw==', 2, 380692)], 
# c: [Share(b'gWoyFQ==', 0, 270418), Share(b'dZaJbQ==', 1, 136633), Share(b'VvyPow==', 2, 26830)]

# Bob: (Share(b'ISLUmg==', 1, 200216), Share(b'x8/YTw==', 1, 336692), Share(b'dZaJbQ==', 1, 136633))
# Charlie: (Share(b'6jH88g==', 2, 345401), Share(b'9B1cQw==', 2, 380692), Share(b'VvyPow==', 2, 26830))
# Alice: (Share(b'5cWs8g==', 0, 377149), Share(b'GTPKrw==', 0, 465161), Share(b'gWoyFQ==', 0, 270418))

### Publishing d/e 0
# Alice: Share(b'WKnj1Q==', 0, 241120),Share(b'fQok4w==', 0, 153108)
# Bob: Share(b'I/VbRw==', 1, 413061),Share(b'0SpaeA==', 1, 276585)
# Charlie: Share(b'uVr85g==', 2, 505585),Share(b'+oqCiw==', 2, 470294)

### Receiving
# Bob: Received d0 from Alice: -> Share(b'WKnj1Q==', 0, 241120)
# Bob: Received d0 from Bob: -> Share(b'I/VbRw==', 1, 413061)
# Bob: Received d0 from Charlie: -> Share(b'uVr85g==', 2, 505585)
# -
# Bob: Received e0 from Alice: -> Share(b'fQok4w==', 0, 153108)
# Bob: Received e0 from Bob: -> Share(b'0SpaeA==', 1, 276585)
# Bob: Received e0 from Charlie: -> Share(b'+oqCiw==', 2, 470294)

# Alice: Received d0 from Alice: -> Share(b'WKnj1Q==', 0, 241120)
# Alice: Received d0 from Bob: -> Share(b'I/VbRw==', 1, 413061)
# Alice: Received d0 from Charlie: -> Share(b'uVr85g==', 2, 505585)
# -
# Alice: Received e0 from Alice: -> Share(b'fQok4w==', 0, 153108)
# Alice: Received e0 from Bob: -> Share(b'0SpaeA==', 1, 276585)
# Alice: Received e0 from Charlie: -> Share(b'+oqCiw==', 2, 470294)


# Charlie: Received d0 from Alice: -> Share(b'WKnj1Q==', 0, 241120)
# Charlie: Received d0 from Bob: -> Share(b'I/VbRw==', 1, 413061)
# Charlie: Received d0 from Charlie: -> Share(b'uVr85g==', 2, 505585)
# -
# Charlie: Received e0 from Alice: -> Share(b'fQok4w==', 0, 153108)
# Charlie: Received e0 from Bob: -> Share(b'0SpaeA==', 1, 276585)
# Charlie: Received e0 from Charlie: -> Share(b'+oqCiw==', 2, 470294)

# -------
# Publishing d/e 1
# Alice: Share(b'gwnDYA==', 0, 373493),Share(b'0tDvqA==', 0, 285481)
# Bob: Share(b'k4Wx6w==', 1, 367007),Share(b'CrUnwA==', 1, 230531)
# Charlie: Share(b'908NGw==', 2, 419266),Share(b'ih9WjQ==', 2, 383975)

### Receiving
# Alice: Received d1 from Alice: -> Share(b'gwnDYA==', 0, 373493)
# Alice: Received d1 from Bob: -> Share(b'k4Wx6w==', 1, 367007)
# Alice: Received d1 from Charlie: -> Share(b'908NGw==', 2, 419266)
# -
# Alice: Received e1 from Alice: -> Share(b'0tDvqA==', 0, 285481)
# Alice: Received e1 from Bob: -> Share(b'CrUnwA==', 1, 230531)
# Alice: Received e1 from Charlie: -> Share(b'ih9WjQ==', 2, 383975)

# Bob: Received d1 from Alice: -> Share(b'gwnDYA==', 0, 373493)
# Bob: Received d1 from Bob: -> Share(b'k4Wx6w==', 1, 367007)
# Bob: Received d1 from Charlie: -> Share(b'908NGw==', 2, 419266)
# -
# Bob: Received e1 from Alice: -> Share(b'0tDvqA==', 0, 285481)
# Bob: Received e1 from Bob: -> Share(b'CrUnwA==', 1, 230531)
# Bob: Received e1 from Charlie: -> Share(b'ih9WjQ==', 2, 383975)

# Charlie: Received d1 from Alice: -> Share(b'gwnDYA==', 0, 373493)
# Charlie: Received d1 from Bob: -> Share(b'k4Wx6w==', 1, 367007)
# Charlie: Received d1 from Charlie: -> Share(b'908NGw==', 2, 419266)
# -
# Charlie: Received e1 from Alice: -> Share(b'0tDvqA==', 0, 285481)
# Charlie: Received e1 from Bob: -> Share(b'CrUnwA==', 1, 230531)
# Charlie: Received e1 from Charlie: -> Share(b'ih9WjQ==', 2, 383975)

# -------
# Publishing d/e 2
# Alice: Share(b'ym+vyg==', 0, 236040),Share(b'ME62Ig==', 0, 148028)
# Bob: Share(b'KFCQlA==', 1, 385263),Share(b'Zy2Ctw==', 1, 248787)
# Charlie: Share(b'NNuKmA==', 2, 17830),Share(b'UArHOg==', 2, 503172)

### Receiving
# Alice: Received d2 from Alice: -> Share(b'ym+vyg==', 0, 236040)
# Alice: Received d2 from Bob: -> Share(b'KFCQlA==', 1, 385263)
# Alice: Received d2 from Charlie: -> Share(b'NNuKmA==', 2, 17830)
# -
# Alice: Received e2 from Alice: -> Share(b'ME62Ig==', 0, 148028)
# Alice: Received e2 from Bob: -> Share(b'Zy2Ctw==', 1, 248787)
# Alice: Received e2 from Charlie: -> Share(b'UArHOg==', 2, 503172)

# Bob: Received d2 from Alice: -> Share(b'ym+vyg==', 0, 236040)
# Bob: Received d2 from Bob: -> Share(b'KFCQlA==', 1, 385263)
# Bob: Received d2 from Charlie: -> Share(b'NNuKmA==', 2, 17830)
# -
# Bob: Received e2 from Alice: -> Share(b'ME62Ig==', 0, 148028)
# Bob: Received e2 from Bob: -> Share(b'Zy2Ctw==', 1, 248787)
# Bob: Received e2 from Charlie: -> Share(b'UArHOg==', 2, 503172)

# Charlie: Received d2 from Alice: -> Share(b'ym+vyg==', 0, 236040)
# Charlie: Received d2 from Bob: -> Share(b'KFCQlA==', 1, 385263)
# Charlie: Received d2 from Charlie: -> Share(b'NNuKmA==', 2, 17830)
# -
# Charlie: Received e2 from Alice: -> Share(b'ME62Ig==', 0, 148028)
# Charlie: Received e2 from Bob: -> Share(b'Zy2Ctw==', 1, 248787)
# Charlie: Received e2 from Charlie: -> Share(b'UArHOg==', 2, 503172)

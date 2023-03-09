"""
Secret sharing scheme.
"""

from __future__ import annotations

from typing import List


class Share:
    """
    A secret share in a finite field.
    """

    def __init__(self, value: int, index: int):
        self.value = value
        self.index = index

    def __repr__(self):
        return f"Share({self.value})"

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
        """Generate a representation suitable for passing in a message."""
        raise NotImplementedError("You need to implement this method.")

    @staticmethod
    def deserialize(serialized) -> Share:
        """Restore object from its serialized representation."""
        raise NotImplementedError("You need to implement this method.")

class Scalar:
    def __init__(self, value: int):
        self.value = value
    def __add__(self, other):
        if isinstance(other, Scalar):
            return Scalar(self.value + other.value) 
        #else, other one is a share    
        #call addition operation of share class 
        return other + self 
    def __repr__(self):
            return f"Scalar({self.value})"
    



def share_secret(secret: int, num_shares: int) -> List[Share]:
    """Generate secret shares."""
    raise NotImplementedError("You need to implement this method.")


def reconstruct_secret(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    raise NotImplementedError("You need to implement this method.")


# Feel free to add as many methods as you want.

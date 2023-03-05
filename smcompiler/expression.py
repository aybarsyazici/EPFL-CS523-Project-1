"""
Tools for building arithmetic expressions to execute with SMC.

Example expression:
>>> alice_secret = Secret()
>>> bob_secret = Secret()
>>> expr = alice_secret * bob_secret * Scalar(2)

MODIFY THIS FILE.
"""

import base64
import random
from typing import Optional


ID_BYTES = 4


def gen_id() -> bytes:
    id_bytes = bytearray(
        random.getrandbits(8) for _ in range(ID_BYTES)
    )
    return base64.b64encode(id_bytes)


class Expression:
    """
    Base class for an arithmetic expression.
    """

    def __init__(
            self,
            id: Optional[bytes] = None
        ):
        # If ID is not given, then generate one.
        if id is None:
            id = gen_id()
        self.id = id

    def __add__(self, other):
        return AddOperation(self, other)

    def __sub__(self, other):
        return SubOperation(self, other);

    def __mul__(self, other):
        return MultOperation(self, other);

    def __hash__(self):
        return hash(self.id)

    # Feel free to add as many methods as you like.      

"""
Below are the different types of expressions
Each has an integer variable denoting the type
0: Scalar
1: Secret
2: Addition
3: Subtraction
4: Multiplication
"""

class Scalar(Expression):
    """Term representing a scalar finite field value."""

    def __init__(
            self,
            value: int,
            id: Optional[bytes] = None
        ):
        self.value = value
        self.type = 0
        super().__init__(id)


    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"


    def __hash__(self):
        return

    # Feel free to add as many methods as you like.


class Secret(Expression):
    """Term representing a secret finite field value (variable)."""

    def __init__(
            self,
            id: Optional[bytes] = None
        ):
        self.type = 1
        super().__init__(id)


    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.value if self.value is not None else ''})"
        )


    # Feel free to add as many methods as you like.


""" A simple class representing the addition of two variables"""
class AddOperation(Expression):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2
        self.type = 2


""" A simple class representing the subtraction of two variables"""
class SubOperation(Expression):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2        
        self.type = 3


""" A simple class representing the multiplication of two variables"""
class MultOperation(Expression):
    def __init__(self, operand1, operand2):
        self.operand1 = operand1
        self.operand2 = operand2  
        self.type = 4

# Feel free to add as many classes as you like.

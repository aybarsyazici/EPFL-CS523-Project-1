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
    
    def prec(self) -> int:
        """Returns the precedence of the expression."""
        if isinstance(self, MultOperation):
            return 2
        elif isinstance(self, AddOperation):
            return 1
        elif isinstance(self, SubOperation):
            return 1
        return 3

    def child_repr(self, child) -> str:
        """Returns a correct representation of the given child expression, wrapping with parentheses if necessary."""
        child_str = repr(child)
        if child.prec() < self.prec():
            return f"({child_str})"
        return child_str

    def __add__(self, other):
        return AddOperation(self, other)

    def __sub__(self, other):
        return SubOperation(self, other);

    def __mul__(self, other):
        return MultOperation(self, other);

    def __hash__(self):
        return hash(self.id)

    def is_term(self) -> bool:
        """Returns true iff the expression is a term."""
        return isinstance(self, Secret) or isinstance(self, Scalar)

    def print_tree_unix(self, indent: int = -1):
        """Prints the expression tree. """
        if(indent >= 0):
            print(" " * indent + "↳", self)
        else:
            print(self)
        if not self.is_term():
            self.left.print_tree_unix(indent + 2)
            self.right.print_tree_unix(indent + 2)
    
    def get_tree_lines(self):
        """Prints the experssion tree like a binary tree showing the left and right childs."""
        # No child.
        if self.is_term():
            line = self.__repr__()
            width = len(line)
            height = 1
            middle = width // 2
            return [line], width, height, middle

        # Two children.
        left, n, p, x = self.left.get_tree_lines()
        right, m, q, y = self.right.get_tree_lines()
        s = self.__repr__()
        u = len(s)
        first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s + y * '_' + (m - y) * ' '
        second_line = x * ' ' + '/' + (n - x - 1 + u + y) * ' ' + '\\' + (m - y - 1) * ' '
        if p < q:
            left += [n * ' '] * (q - p)
        elif q < p:
            right += [m * ' '] * (p - q)
        zipped_lines = zip(left, right)
        lines = [first_line, second_line] + [a + u * ' ' + b for a, b in zipped_lines]
        return lines, n + m + u, max(p, q) + 2, n + u // 2
    
    def print_tree(self):
        lines, *_ = self.get_tree_lines()
        for line in lines:
            print(line)



class Scalar(Expression):
    """Term representing a scalar finite field value."""

    def __init__(
            self,
            value: int,
            id: Optional[bytes] = None
        ):
        self.value = value
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
            value: Optional[int] = None,
            id: Optional[bytes] = None
        ):
        self.value = value
        super().__init__(id)


    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.value if self.value is not None else ''})"
        )


    # Feel free to add as many methods as you like.

""" A simple class representing the addition of two variables"""
class AddOperation(Expression):
    def __init__(self, operand1, operand2):
        self.left = operand1
        self.right = operand2
    def __repr__(self):
        return f"{self.child_repr(self.left)} + {self.child_repr(self.right)}"


""" A simple class representing the subtraction of two variables"""
class SubOperation(Expression):
    def __init__(self, operand1, operand2):
        self.left = operand1
        self.right = operand2   
    def __repr__(self):
        return f"{self.child_repr(self.left)} - {self.child_repr(self.right)}"     


""" A simple class representing the multiplication of two variables"""
class MultOperation(Expression):
    def __init__(self, operand1, operand2):
        self.left = operand1
        self.right = operand2  
    def __repr__(self):
        return f"{self.child_repr(self.left)} * {self.child_repr(self.right)}"  

# Feel free to add as many classes as you like.

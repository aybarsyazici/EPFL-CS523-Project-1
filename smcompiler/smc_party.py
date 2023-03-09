"""
Implementation of an SMC client.

MODIFY THIS FILE.
"""
# You might want to import more classes if needed.

import collections
import json
from typing import (
    Dict,
    Set,
    Tuple,
    Union
)

from communication import Communication
from expression import (
    Expression,
    Secret,
    Scalar,
    AddOperation,
    MultOperation, 
    SubOperation
)
from protocol import ProtocolSpec
from secret_sharing import(
    reconstruct_secret,
    share_secret,
    Share,
)

# Feel free to add as many imports as you want.


class SMCParty:
    """
    A client that executes an SMC protocol to collectively compute a value of an expression together
    with other clients.

    Attributes:
        client_id: Identifier of this client
        server_host: hostname of the server
        server_port: port of the server
        protocol_spec (ProtocolSpec): Protocol specification
        value_dict (dict): Dictionary assigning values to secrets belonging to this client.
    """

    def __init__(
            self,
            client_id: str,
            server_host: str,
            server_port: int,
            protocol_spec: ProtocolSpec,
            value_dict: Dict[Secret, int]
        ):
        self.comm = Communication(server_host, server_port, client_id)

        self.client_id = client_id
        self.protocol_spec = protocol_spec
        self.value_dict = value_dict


    def run(self) -> int:
        """
        The method the client use to do the SMC.
        """
        raise NotImplementedError("You need to implement this method.")


    # Suggestion: To process expressions, make use of the *visitor pattern* like so:
    def process_expression(
            self,
            expr: Expression
        ):

        #TODO consider using match-case statement
        if isinstance(expr, Scalar):          # if expr is a scalar, return the value of scalar
            return self.handle_scalar(expr)
        elif isinstance(expr, Secret):        
            return self.handle_secret(expr)          #this is a placeholder TODO talk about this line
        elif isinstance(expr, AddOperation):        #if expression is addition, add its operands
            return self.handle_add(expr)
        elif isinstance(expr, SubOperation):       #if expression is sub, subtract its operands
            return self.handle_sub(expr)
        elif isinstance(expr, MultOperation): 
            return self.handle_mult(expr)
        # Call specialized methods for each expression type, and have these specialized
        # methods in turn call `process_expression` on their sub-expressions to process
        # further.

    # Feel free to add as many methods as you want.

    #TODO implement these methods
    def handle_scalar(self, expression):
        return expression.value
    def handle_secret(self, expression):
        pass
    def handle_add(self, expression):
        return self.process_expression(expression.operand1) + self.process_expression(expression.operand2)
    def handle_sub(self, expression):
        return self.process_expression(expression.operand1) - self.process_expression(expression.operand2)
    def handle_mult(self, expression):
        pass
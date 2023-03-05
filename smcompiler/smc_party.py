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
    Secret
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
        if expr.type == 0:          # if expr is a scalar, return the value of scalar
            return expr.value
        elif expr.type == 1:        
            return 1                #this is a placeholder TODO talk about this line
        elif expr.type == 2:        #if expression is addition, add its operands
            return self.process_expression(expr.operand1) + self.process_expression(expr.operand2)
        elif expr.type == 3:       #if expression is addition, subtract its operands
            return self.process_expression(expr.operand1) - self.process_expression(expr.operand2)
        elif expr.type == 4: 
            return 4 #placeholder TODO implement beaver triplet
        # Call specialized methods for each expression type, and have these specialized
        # methods in turn call `process_expression` on their sub-expressions to process
        # further.
        pass

    # Feel free to add as many methods as you want.

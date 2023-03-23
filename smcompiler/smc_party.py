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
    reconstruct_shares,
    publish_result,
    retrieve_share,
    send_share,
    gen_share,
    Share,
    receive_public_results,
    get_beaver_triplet,
    publish_triplet,
    get_all_triplets,
)
import time
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
        self.beaver_triplets = None
        self.client_id = client_id
        self.protocol_spec = protocol_spec
        self.value_dict = value_dict
        self.tripletIndex = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.elapsed_time = 0



    def run(self) -> int:
        # Implementation of SMC protocol
        # Iterate over the secrets that this party is responsible for.
        # join ttp
        # publish i joined msg
        # check for other participants
        start = time.time()
        print('Expression',self.protocol_spec.expr)
        for secret in self.value_dict:
            # create shares of the secret
            shares = gen_share(self.value_dict[secret], len(self.protocol_spec.participant_ids))
            print(f"SMCParty: {self.client_id} has created shares for secret {secret.id} -> {shares}")
            for participant, share in zip(self.protocol_spec.participant_ids, shares):
                # send share to participant using self.comm.send_private_message
                #then, add the amount of bytes sent for evaluation part
                self.bytes_sent += send_share(share, participant, secret.id, self.comm)
        # Process the expression
        result_share = self.process_expression(self.protocol_spec.expr)
        assert isinstance(result_share, Share)
        print(f"SMCParty: {self.client_id} has found the result share!")
        # Publish the result share.
        self.bytes_sent += publish_result(result_share, self.comm)
        # Retrieve the other resulting shares.
        all_result_shares, byte_count = receive_public_results(self.comm,self.protocol_spec.participant_ids)
        self.bytes_received += byte_count
        print(f"SMCParty: {self.client_id} has retrieved ALL shares", all_result_shares)
        reconstructed = reconstruct_shares(all_result_shares)
        self.elapsed_time = time.time() - start
        # Return the reconstructed results with the calculated metrics
        return (reconstructed)


    # Suggestion: To process expressions, make use of the *visitor pattern* like so:
    def process_expression(
            self,
            expr: Expression
        ):
        print("PROCESS EXPR: ", expr)
        #TODO consider using match-case statement
        if isinstance(expr, Scalar):          # if expr is a scalar, return the value of scalar
            return self.handle_scalar(expr)
        elif isinstance(expr, Secret):        
            return self.handle_secret(expr)          
        elif isinstance(expr, AddOperation):        #if expression is addition, add its operands
            return self.handle_add(expr)
        elif isinstance(expr, SubOperation):       
            return self.handle_sub(expr)
        elif isinstance(expr, MultOperation): 
            return self.handle_mult(expr)

    def handle_scalar(self, expression):
        return expression.value
    def handle_secret(self, expression):
        return retrieve_share(expression.id, self.comm)
    def handle_add(self, expression):
        leftSide = self.process_expression(expression.left)
        rightSide = self.process_expression(expression.right)
        return leftSide + rightSide
    def handle_sub(self, expression):
        leftSide = self.process_expression(expression.left)
        rightSide = self.process_expression(expression.right)
        return leftSide - rightSide
    def handle_mult(self, expression):
        l_expression = self.process_expression(expression.left)
        r_expression = self.process_expression(expression.right)
        if isinstance(l_expression, Share) and isinstance(r_expression, Share):
            # Beaver Triplet logic
            if l_expression.beaver_triplets is None:
                if self.beaver_triplets is None:
                    self.beaver_triplets = get_beaver_triplet(comm=self.comm, secret_id=self.tripletIndex)
                l_expression.beaver_triplets = self.beaver_triplets
                # Each party locally computes a share of d = s - a
                d_share = Share(index=l_expression.index, value=((l_expression.value - l_expression.beaver_triplets[0].value)%520633))
                # Each party locally computes a share of e = v - b
                e_share = Share(index=r_expression.index, value=((r_expression.value - l_expression.beaver_triplets[1].value)%520633))
                # broadcast d and e to all parties
                self.bytes_sent += publish_triplet(d_share, self.comm, "d", self.tripletIndex)
                self.bytes_sent += publish_triplet(e_share, self.comm, "e", self.tripletIndex)
                # Get all the d and e values
                (d,e,byte_count) = get_all_triplets(comm=self.comm, participant_ids=self.protocol_spec.participant_ids, secret_id=self.tripletIndex)
                self.bytes_received += byte_count
                l_expression.d = d
                l_expression.e = e
                self.tripletIndex += 1
        return l_expression * r_expression
from math import sqrt
from communication import Communication

from expression import (
    Expression,
    Secret,
    Scalar,
    AddOperation,
    MultOperation,
    SubOperation,
)

from secret_sharing import (
    Share,
    gen_share,
    send_share,
    retrieve_share,
    get_all_triplets,
    get_beaver_triplet,
    publish_triplet,
    reconstruct_shares,
    publish_result_for_class,
    receive_public_results_for_class
)

class Class:
    # Represents the class students belong to
    # it has a list of lectures and a list of students

    # Constuctor
    def __init__(self, lectures: list, students: list):
        self.lectures = lectures
        self.students = students

class Student():
    
    # Constuctor
    # Contains the id of the student, the class he belongs to and the values of the secrets he has
    # We'll try to fill means and standard_deviation dictionaries by using SMC
    def __init__(self, client_id, server_host, server_port, cl: Class, value_dict):
        self.comm = Communication(server_host, server_port, client_id)
        self.client_id = client_id
        self.cl = cl
        self.value_dict = value_dict
        self.shares = {}
        self.means = {}
        self.standard_deviations = {}
        self.tripletIndex = 0

    
    def share_secrets(self):
        for secret in self.value_dict:
            # create shares of the secret
            shares = gen_share(self.value_dict[secret], len(self.cl.students), secret.id)
            print(f"Class: {self.client_id} has created shares for secret {secret.id} -> {shares}")
            for participant, share in zip(self.cl.students, shares):
                # send share to participant using self.comm.send_private_message
                send_share(share, participant, secret.id, self.comm)
            
    def get_shares(self):
        for student in self.cl.students:
            if student == self.client_id:
                pass
            if student not in self.shares:
                self.shares[student] = {}
            for lecture in self.cl.lectures:
                id = f'{lecture}/{student}'
                print(f'Class: {self.client_id} Trying to retrieve:{id.encode()}')
                share = retrieve_share(id.encode(), self.comm)
                self.shares[student][lecture] = share

    
    def compute_mean(self):
        # For each lecture in the class
        for lecture in self.cl.lectures:
            # Create a list of shares of the lecture
            shares = []
            for student in self.cl.students:
                shares.append(self.shares[student][lecture])
            print(f'Class: {self.client_id} has shares for lecture {lecture} -> {shares}')
            # Sum all the shares
            sum = 0
            for share in shares:
                sum += share
            # Publish the result
            publish_result_for_class(sum, self.comm, lecture, 'mean')
        # Get all the results
        for lecture in self.cl.lectures:
            public_shares = receive_public_results_for_class(self.comm, self.cl.students, lecture, 'mean')
            # Reconstruct the result
            result = reconstruct_shares(public_shares)
            # Store the result
            self.means[lecture] = result
            print(f"Class: {self.client_id} has computed the mean of lecture {lecture} -> {result}")
        
    def std_dev(self):
        # For each lecture in the class
        for lecture in self.cl.lectures:
            # Create a list of shares of the lecture
            shares = []
            for student in self.cl.students:
                shares.append(self.shares[student][lecture])
            print(f'Class: {self.client_id} has shares for lecture {lecture} -> {shares}')
            # Compute the standard variance
            # first compute for all the shares the difference between the share and the mean
            # then square the result
            # then sum all the results
            # then publish the result
            sum = 0
            student_count = len(self.cl.students)
            for share in shares:
                sum += self.handle_mult((student_count*share - self.means[lecture]),(student_count*share - self.means[lecture]))
            # Publish the result
            print(f'Class: {self.client_id} has computed the SUM VAR     of lecture {lecture} -> {sum}')
            publish_result_for_class(sum, self.comm, lecture, 'variance')
        # Get all the results
        for lecture in self.cl.lectures:
            public_shares = receive_public_results_for_class(self.comm, self.cl.students, lecture, 'variance')
            # Reconstruct the result
            result = reconstruct_shares(public_shares)
            # Store the result
            self.standard_deviations[lecture] = sqrt(result/(student_count*student_count*(len(self.cl.students))))
            print(f"Class: {self.client_id} has computed the variance of lecture {lecture} -> {result}")
    
    def run(self):
        self.share_secrets()
        self.get_shares()
        print(f'Class {self.client_id} has shares: {self.shares}')
        self.compute_mean()
        print(f'Class {self.client_id} has means: {self.means}')
        self.std_dev()
        # before returning the mean, divide all the means by the number of students
        toReturn = self.means
        for lecture in self.cl.lectures:
            toReturn[lecture] = toReturn[lecture]/len(self.cl.students)
        return (toReturn, self.standard_deviations)
        
    def handle_mult(self, l_expression, r_expression):
        if isinstance(l_expression, Share) and isinstance(r_expression, Share):
            # Beaver Triplet logic
            if l_expression.beaver_triplets is None:
                l_expression.beaver_triplets = get_beaver_triplet(comm=self.comm,secret_id=self.tripletIndex)
                # Each party locally computes a share of d = s - a
                d_share = Share(index=l_expression.index, value=((l_expression.value - l_expression.beaver_triplets[0].value)))
                # Each party locally computes a share of e = v - b
                e_share = Share(index=r_expression.index, value=((r_expression.value - l_expression.beaver_triplets[1].value)))
                # broadcast d and e to all parties
                print(f'Class: {self.client_id} publishing d/e {d_share},{e_share}')
                publish_triplet(d_share, self.comm, "d", self.tripletIndex)
                publish_triplet(e_share, self.comm, "e", self.tripletIndex)
                # Get all the d and e values
                (d,e) = get_all_triplets(comm=self.comm, participant_ids=self.cl.students, secret_id=self.tripletIndex)
                l_expression.d = d
                l_expression.e = e
                self.tripletIndex += 1
        return l_expression * r_expression

        
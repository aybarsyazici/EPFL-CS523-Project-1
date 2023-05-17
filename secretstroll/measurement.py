import time
import sys

class Measurement:

    def __init__(self):
        self.delta_t = 0
        self.bytes_out = 0

    def update(self, delta_t, bytes_out):   
        self.delta_t += delta_t
        self.bytes_out += bytes_out

def measured(f, measurement):
    def wrapper(*args, **kwargs):
        #Measure time
        t = time.time()
        out = f(*args, **kwargs)
        dt = time.time() - t
        #Measure output size
        bytes_out = sys.getsizeof(out)
        #Update the measurement object
        measurement.update(dt, bytes_out)
        return out
    return wrapper    



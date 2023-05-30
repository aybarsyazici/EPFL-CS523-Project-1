import time
import sys
import jsonpickle

class Measurement:

    def __init__(self):
        self.delta_t = []
        self.bytes_out = []

    """
    Append single measurement values to the arrays
    """
    def updateSingle(self, delta_t, bytes_out):   
        self.delta_t.append(delta_t)
        self.bytes_out.append(bytes_out)

    """
    Update measurement arrays with multiple values passed as arrays
    """
    def updateArray(self, delta_t, bytes_out):
        self.delta_t += delta_t
        self.bytes_out += bytes_out     

def measured(f, measurement):
    def wrapper(*args, **kwargs):
        #Measure time
        t = time.time()
        out = f(*args, **kwargs)
        dt = (time.time() - t)*1000
        #Measure output size
        output_str = jsonpickle.encode(out, unpicklable=False)
        bytes_out = len(output_str)       
        #Update the measurement object
        measurement.updateSingle(dt, bytes_out)
        return out
    return wrapper

def getsize(o):
    size = 0
    objects = [o]
    ids = set()
    while objects:
        new = []
        for object in objects:
            if id(object) not in ids:
                ids.add(id(object))
                size += sys.getsizeof(object)
                new.append(object)
                print(sys.getsizeof(object))
        print('')        
        objects = gc.get_referents(*new)        
    return size    

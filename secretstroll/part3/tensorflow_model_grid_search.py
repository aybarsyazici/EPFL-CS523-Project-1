import data_sanitize
import importlib
import pandas as pd
from tensorflow.keras.layers import Dense, BatchNormalization, Dropout
from tensorflow.keras.models import Sequential
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.feature_selection import SelectFromModel
from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler
from joblib import Parallel, delayed
import multiprocessing

traces = data_sanitize.get_traces()
training_data = data_sanitize.get_training_data(traces)
# convert the training data which is a numpy array of shape(5000,11) to a pandas dataframe
df = pd.DataFrame(training_data, columns=[
    'grid',
    'num_outgoing',
    'num_incoming',
    'outgoing_ratio',
    'incoming_ratio',
    'outgoing_bytes',
    'incoming_bytes',
    'avg_outgoing_freq',
    'avg_incoming_freq',
    'std_outgoing_freq',
    'std_incoming_freq',
    'avg_outgoing_bytes',
    'avg_incoming_bytes',
    'std_outgoing_bytes',
    'std_incoming_bytes',
    'min_outgoing_bytes',
    'min_incoming_bytes',
    'max_outgoing_bytes',
    'max_incoming_bytes',
    'min_outgoing_freq',
    'min_incoming_freq',
    'max_outgoing_freq',
    'max_incoming_freq'
])

label_count = len(df['grid'].unique())

X = df.drop('grid', axis=1)
y = df['grid']

# stratify the data to ensure that the training and testing sets have the same distribution of grids
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y)
# split the train into train and validation sets
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, stratify=y_train)

# Scale the data
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)

class Layer:
    type: str
    value: int
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
    def __str__(self):
        return f'{self.type}({self.value})'
    
    # serialize the layer to a string
    def serialize(self):
        return f'{self.type}({self.value})'
    
    # deserialize the layer from a string
    @staticmethod
    def deserialize(layer_string):
        layer_type = layer_string.split('(')[0]
        layer_value = int(layer_string.split('(')[1].split(')')[0])
        return Layer(layer_type, layer_value)

layers_list = [
    #16 and 32 neurons combined
    [Layer('dense', 16), Layer('batchnorm', 16), Layer('dense', 16), Layer('dense', 16)],
    [Layer('dense', 16), Layer('batchnorm', 16), Layer('dense', 16)],
    [Layer('dense', 16), Layer('batchnorm', 16)],
    [Layer('dense', 16)],
    [Layer('dense', 16), Layer('batchnorm', 32), Layer('dense', 32), Layer('dense', 32)],
    [Layer('dense', 16), Layer('batchnorm', 32), Layer('dense', 32)],
    [Layer('dense', 16), Layer('batchnorm', 32)],
    [Layer('dense', 16)],
    [Layer('dense', 16), Layer('batchnorm', 16), Layer('dense', 16), Layer('dense', 32)],
    [Layer('dense', 16), Layer('batchnorm', 16), Layer('dense', 32)],
    #32 neurons
    [Layer('dense', 32), Layer('batchnorm', 32), Layer('dense', 32), Layer('dense', 32)],
    [Layer('dense', 32), Layer('batchnorm', 32), Layer('dense', 32)],
    [Layer('dense', 32), Layer('batchnorm', 32)],
    [Layer('dense', 32)],
    #64 neurons
    [Layer('dense', 64), Layer('batchnorm', 64), Layer('dense', 64), Layer('dense', 64)],
    [Layer('dense', 64), Layer('batchnorm', 64), Layer('dense', 64)],
    [Layer('dense', 64), Layer('batchnorm', 64)],
    [Layer('dense', 64)],
    [Layer('dense', 128), Layer('batchnorm', 128), Layer('dense', 128), Layer('dense', 128)],
    [Layer('dense', 128), Layer('batchnorm', 128), Layer('dense', 128)],
    [Layer('dense', 128), Layer('batchnorm', 128)],
    [Layer('dense', 128)],
    [Layer('dense', 256), Layer('batchnorm', 256), Layer('dense', 256), Layer('dense', 256)],
    [Layer('dense', 256), Layer('batchnorm', 256), Layer('dense', 256)],
    [Layer('dense', 256), Layer('batchnorm', 256)],
    [Layer('dense', 256)],
    # without batch normalization
    [Layer('dense', 32), Layer('dense', 32), Layer('dense', 32), Layer('dense', 32)],
    [Layer('dense', 32), Layer('dense', 32), Layer('dense', 32)],
    [Layer('dense', 32), Layer('dense', 32)],
    [Layer('dense', 32)],
    [Layer('dense', 64), Layer('dense', 64), Layer('dense', 64), Layer('dense', 64)],
    [Layer('dense', 64), Layer('dense', 64), Layer('dense', 64)],
    [Layer('dense', 64), Layer('dense', 64)],
    [Layer('dense', 64)],
    [Layer('dense', 128), Layer('dense', 128), Layer('dense', 128), Layer('dense', 128)],
    [Layer('dense', 128), Layer('dense', 128), Layer('dense', 128)],
    [Layer('dense', 128), Layer('dense', 128)],
    [Layer('dense', 128)],
    # with dropout and batch normalization
    # 16 and 32 neurons combined
    [Layer('dense', 16), Layer('batchnorm', 16), Layer('dropout', 0.2), Layer('dense', 16), Layer('batchnorm', 16), Layer('dropout', 0.2), Layer('dense', 16), Layer('batchnorm', 16), Layer('dropout', 0.2), Layer('dense', 16), Layer('batchnorm', 16), Layer('dropout', 0.2)],
    [Layer('dense', 16), Layer('batchnorm', 16), Layer('dropout', 0.2), Layer('dense', 16), Layer('batchnorm', 16), Layer('dropout', 0.2), Layer('dense', 16), Layer('batchnorm', 16), Layer('dropout', 0.2)],
    [Layer('dense', 16), Layer('batchnorm', 16), Layer('dropout', 0.2), Layer('dense', 16), Layer('batchnorm', 16), Layer('dropout', 0.2)],
    [Layer('dense', 16), Layer('batchnorm', 16), Layer('dropout', 0.2)],
    [Layer('dense', 16), Layer('batchnorm', 32), Layer('dropout', 0.2), Layer('dense', 32), Layer('batchnorm', 32), Layer('dropout', 0.2), Layer('dense', 32), Layer('batchnorm', 32), Layer('dropout', 0.2), Layer('dense', 32), Layer('batchnorm', 32), Layer('dropout', 0.2)],
    [Layer('dense', 16), Layer('batchnorm', 32), Layer('dropout', 0.2), Layer('dense', 32), Layer('batchnorm', 32), Layer('dropout', 0.2), Layer('dense', 32), Layer('batchnorm', 32), Layer('dropout', 0.2)],
    [Layer('dense', 16), Layer('batchnorm', 32), Layer('dropout', 0.2), Layer('dense', 32), Layer('batchnorm', 32), Layer('dropout', 0.2)],
    [Layer('dense', 16), Layer('batchnorm', 32), Layer('dropout', 0.2)],
    [Layer('dense', 32), Layer('batchnorm', 32), Layer('dropout', 0.2), Layer('dense', 32), Layer('batchnorm', 32), Layer('dropout', 0.2), Layer('dense', 32), Layer('batchnorm', 32), Layer('dropout', 0.2), Layer('dense', 32), Layer('batchnorm', 32), Layer('dropout', 0.2)],
    [Layer('dense', 32), Layer('batchnorm', 32), Layer('dropout', 0.2), Layer('dense', 32), Layer('batchnorm', 32), Layer('dropout', 0.2), Layer('dense', 32), Layer('batchnorm', 32), Layer('dropout', 0.2)],
    [Layer('dense', 32), Layer('batchnorm', 32), Layer('dropout', 0.2), Layer('dense', 32), Layer('batchnorm', 32), Layer('dropout', 0.2)],
    [Layer('dense', 32), Layer('batchnorm', 32), Layer('dropout', 0.2)],
    [Layer('dense', 64), Layer('batchnorm', 64), Layer('dropout', 0.2), Layer('dense', 64), Layer('batchnorm', 64), Layer('dropout', 0.2), Layer('dense', 64), Layer('batchnorm', 64), Layer('dropout', 0.2), Layer('dense', 64), Layer('batchnorm', 64), Layer('dropout', 0.2)],
    [Layer('dense', 64), Layer('batchnorm', 64), Layer('dropout', 0.2), Layer('dense', 64), Layer('batchnorm', 64), Layer('dropout', 0.2), Layer('dense', 64), Layer('batchnorm', 64), Layer('dropout', 0.2)],
    [Layer('dense', 64), Layer('batchnorm', 64), Layer('dropout', 0.2), Layer('dense', 64), Layer('batchnorm', 64), Layer('dropout', 0.2)],
    [Layer('dense', 64), Layer('batchnorm', 64), Layer('dropout', 0.2)],
    [Layer('dense', 128), Layer('batchnorm', 128), Layer('dropout', 0.2), Layer('dense', 128), Layer('batchnorm', 128), Layer('dropout', 0.2), Layer('dense', 128), Layer('batchnorm', 128), Layer('dropout', 0.2), Layer('dense', 128), Layer('batchnorm', 128), Layer('dropout', 0.2)],
    [Layer('dense', 128), Layer('batchnorm', 128), Layer('dropout', 0.2), Layer('dense', 128), Layer('batchnorm', 128), Layer('dropout', 0.2), Layer('dense', 128), Layer('batchnorm', 128), Layer('dropout', 0.2)],
    [Layer('dense', 128), Layer('batchnorm', 128), Layer('dropout', 0.2), Layer('dense', 128), Layer('batchnorm', 128), Layer('dropout', 0.2)],
    [Layer('dense', 128), Layer('batchnorm', 128), Layer('dropout', 0.2)],
]

class SavedModels:
    accuracy = 0
    model = None
    layers = None

# number of cores
num_cores = multiprocessing.cpu_count()
best_models = []
for i in range(num_cores):
    best_models.append(SavedModels())


# training one layer
def train_model(layers):
    # create model
    model = Sequential()
    for layer in layers:
        if layer.type == 'dense':
            model.add(Dense(layer.value, activation='relu'))
        elif layer.type == 'dropout':
            model.add(Dropout(layer.value))
        elif layer.type == 'batchnorm':
            model.add(BatchNormalization())
    model.add(Dense(label_count, activation='softmax'))

    # compile model
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['sparse_categorical_accuracy'])

    # train model
    model.fit(X_train, y_train, epochs=100, batch_size=32, verbose=0)

    # evaluate the model
    _, accuracy = model.evaluate(X_val, y_val, verbose=0)
    # save model if it is better than the previous best
    if accuracy > best_models[i].accuracy:
        best_models[i].accuracy = accuracy
        best_models[i].model = model
        best_models[i].layers = layers

    return accuracy

def train_chunk(chunk):
    bestModel = SavedModels()
    for i, layers in enumerate(chunk):
        accuracy = train_model(layers)
        if accuracy > bestModel.accuracy:
            bestModel.accuracy = accuracy
            bestModel.model = best_models[i].model
            bestModel.layers = best_models[i].layers
    return bestModel

import numpy as np
# number of cores
num_cores = multiprocessing.cpu_count()

# Divide the layers list into equal chunks
layers_chunks = np.array_split(layers_list, num_cores)

# main 
if __name__ == '__main__':
    # Each core will train ONE chunk
    best_models = Parallel(n_jobs=num_cores)(delayed(train_chunk)(chunk) for chunk in layers_chunks)
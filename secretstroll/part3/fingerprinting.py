import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import data_sanitize
from tqdm import tqdm
def classify(train_features, train_labels, test_features, test_labels):

    """Function to perform classification, using a 
    Random Forest. 

    Reference: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
    
    Args:
        train_features (numpy array): list of features used to train the classifier
        train_labels (numpy array): list of labels used to train the classifier
        test_features (numpy array): list of features used to test the classifier
        test_labels (numpy array): list of labels (ground truth) of the test dataset

    Returns:

        predictions: list of labels predicted by the classifier for test_features

    Note: You are free to make changes the parameters of the RandomForestClassifier().
    """
    
    # best params from grid search
    best_params = {
        'n_estimators': 400,
        'max_depth': 20,
        'max_features': None,
        'min_samples_leaf': 1,
        'min_samples_split': 2,
    }
    # Initialize a random forest classifier. Change parameters if desired.
    clf = RandomForestClassifier(**best_params)
    # Scale the features.
    scaler = StandardScaler()
    train_features = scaler.fit_transform(train_features)
    test_features = scaler.transform(test_features)
    # Select the most important features.
    selector = SelectFromModel(RandomForestClassifier().fit(train_features, train_labels), prefit=True)
    train_features = selector.transform(train_features)
    test_features = selector.transform(test_features)
    # Train the classifier using the training features and labels.
    clf.fit(train_features, train_labels)
    # Use the classifier to make predictions on the test features.
    predictions = clf.predict(test_features)
    
    return predictions

def perform_crossval(features, labels, folds=10):

    """Function to perform cross-validation.
    Args:
        features (list): list of features
        labels (list): list of labels
        folds (int): number of fold for cross-validation (default=10)
    Returns:
        You can modify this as you like.
    
    This function splits the data into training and test sets. It feeds
    the sets into the classify() function for each fold. 

    You need to use the data returned by classify() over all folds 
    to evaluate the performance.         
    """

    # Initialize a stratified k-fold object for cross-validation. 
    # You can use a different number of folds if you want.
    skf = StratifiedKFold(n_splits=folds)
    # Initialize lists to store the results of classification.
    accuracy = []
    precision = []
    recall = []
    f1 = []
    i = 0
    # Loop over the folds.
    for train_index, test_index in tqdm(skf.split(features, labels), desc="Cross Validation"):
        # Split the data into training and test sets.
        train_features, test_features = np.array(features)[train_index], np.array(features)[test_index]
        train_labels, test_labels = np.array(labels)[train_index], np.array(labels)[test_index]
        # Perform classification.
        predictions = classify(train_features, train_labels, test_features, test_labels)
        # Compute metrics.
        accuracy.append(accuracy_score(test_labels, predictions))
        precision.append(precision_score(test_labels, predictions, average='macro'))
        recall.append(recall_score(test_labels, predictions, average='macro'))
        f1.append(f1_score(test_labels, predictions, average='macro'))
        # Print the metrics for the current fold.
        i += 1
        print()
        print(f"Metrics for fold {i}:")
        print(f"\tAccuracy: {accuracy[-1]}")
        print(f"\tPrecision: {precision[-1]}")
        print(f"\tRecall: {recall[-1]}")
        print(f"\tF1: {f1[-1]}")
    # Print the average metrics.
    print("\nAverage metrics:")
    print("\tAccuracy: ", np.mean(accuracy))
    print("\tPrecision: ", np.mean(precision))
    print("\tRecall: ", np.mean(recall))
    print("\tF1: ", np.mean(f1))



def load_data():

    """Function to load data that will be used for classification.

    Args:
        You can provide the args you want.
    Returns:
        features (list): the list of features you extract from every trace
        labels (list): the list of identifiers for each trace
    
    An example: Assume you have traces (trace1...traceN) for cells with IDs in the
    range 1-N.  
    
    You extract a list of features from each trace:
    features_trace1 = [f11, f12, ...]
    .
    .
    features_traceN = [fN1, fN2, ...]

    Your inputs to the classifier will be:

    features = [features_trace1, ..., features_traceN]
    labels = [1, ..., N]

    Note: You will have to decide what features/labels you want to use and implement 
    feature extraction on your own.
    """
    training_data = data_sanitize.get_saved_training_data()
    # 0th index is the label, rest are features
    features = [x[1:] for x in training_data]
    labels = [x[0] for x in training_data]

    return features, labels
        
def main():

    """Please complete this skeleton to implement cell fingerprinting.
    This skeleton provides the code to perform classification 
    using a Random Forest classifier. You are free to modify the 
    provided functions as you wish.

    Read about random forests: https://towardsdatascience.com/understanding-random-forest-58381e0602d2
    """

    features, labels = load_data()
    perform_crossval(features, labels, folds=10)
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
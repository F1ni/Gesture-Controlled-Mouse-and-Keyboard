import numpy as np
from sklearn.model_selection import train_test_split
import time

randomstate = 5  # is a random seed used for reproducibility.
dataset = "Model/gestures.csv"  # csv file path
modelsavepath = "Model/model"  # path of where to save model

numberofgestures = 5  # number of gestures to detect so the correct number of output nodes will be used
X_dataset = np.loadtxt(dataset, delimiter=',', dtype='float32', usecols=(range(1, 43)))  # gestures.csv
# ^ loads the csv file text using only columns 2, 43. the np.loadtxt will load it into a numpy array
y_dataset = np.loadtxt(dataset, delimiter=',', dtype='int32', usecols=0)  # gesture labels.csv
# ^ loads the corresponding labels from the first column in the dataset
X_train, X_test, y_train, y_test = train_test_split(X_dataset, y_dataset, train_size=0.75, random_state=randomstate)  #


class NeuralNetwork():
    def __init__(self, sizes, epochs=1000, learning_rate=0.001):
        self.sizes = sizes
        self.epochs = epochs
        self.l_rate = learning_rate

        # we save all parameters in the neural network in this dictionary
        self.params = self.initialisation()

    def sigmoid(self, x, derivative=False):
        if derivative:
            return np.exp(-x) / ((np.exp(-x) + 1) ** 2)
        return 1 / (1 + np.exp(-x))

    def softmax(self, x, derivative=False):
        exps = np.exp(x - x.max())
        if derivative:
            return exps / np.sum(exps, axis=0) * (1 - exps / np.sum(exps, axis=0))
        return exps / np.sum(exps, axis=0)
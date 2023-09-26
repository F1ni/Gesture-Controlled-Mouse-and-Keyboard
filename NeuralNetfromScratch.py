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

    def ReLU(self, x, derivative=False):
        if derivative:
            if x <= 0:
                return 0
            else:
                return 1
        if x <= 0:
            return 0
        else:
            return x

    def sigmoid(self, x, derivative=False):
        if derivative:
            return np.exp(-x) / ((np.exp(-x) + 1) ** 2)
        return 1 / (1 + np.exp(-x)) # if differentiate this tehn you get the thing above

    def softmax(self, x, derivative=False):
        exps = np.exp(x - x.max())
        if derivative:
            return exps / np.sum(exps, axis=0) * (1 - exps / np.sum(exps, axis=0))
        return exps / np.sum(exps, axis=0)

    def initialisation(self):
        input_layer = self.sizes[0]
        hidden_1 = self.sizes[1]
        hidden_2 = self.sizes[2]
        output_layer = self.sizes[3]

        params = {
            "W1": np.random.randn(hidden_1, output_layer) * np.sqrt(1. / hidden_1),
            "W2": np.random.randn(hidden_2, hidden_1) * np.sqrt(1. / hidden_2),
            "W3": np.random.randn(output_layer, hidden_2) * np.sqrt(1. / output_layer)
        }

        return params

    def forward_pass(self, x_train):
        params = self.params

        # input layer activations become sample
        params['A0'] = x_train

        # input layer to hidden layer 1
        params['Z1'] = np.dot(params["W1"], params['A0'])
        params['A1'] = self.sigmoid(params["Z1"])

        # hidden layer 1 to hidden layer 2
        params['Z2'] = np.dot(params["W2"], params['A1'])
        params['A2'] = self.sigmoid(params['Z2'])

        # hidden layer 2 to output layer
        params['Z3'] = np.dot(params["W3"], params['A2'])
        params['A3'] = self.softmax(params['Z3'])

        return params['A3']

    def backward_pass(self, y_train, output):
        """
            This is the backpropagation algorithm, for calculating the updates
            of the neural network's parameters.

            Note: There is a stability issue that causes warnings. This is
                  caused  by the dot and multiply operations on the huge arrays.

                  RuntimeWarning: invalid value encountered in true_divide
                  RuntimeWarning: overflow encountered in exp
                  RuntimeWarning: overflow encountered in square
        """
        params = self.params
        change_w = {}

        # Calculate W3 update
        error = 2 * (output - y_train) / output.shape[0] * self.softmax(params['Z3'], derivative=True)
        change_w['W3'] = np.outer(error, params['A2'])

        # Calculate W2 update
        error = np.dot(params['W3'].T, error) * self.sigmoid(params['Z2'], derivative=True)
        change_w['W2'] = np.outer(error, params['A1'])

        # Calculate W1 update
        error = np.dot(params['W2'].T, error) * self.sigmoid(params['Z1'], derivative=True)
        change_w['W1'] = np.outer(error, params['A0'])

        return change_w

    def update_network_parameters(self, changes_to_w):
        """
            Update network parameters according to update rule from
            Stochastic Gradient Descent.

            θ = θ - η * ∇J(x, y),
                theta θ:            a network parameter (e.g. a weight w)
                eta η:              the learning rate
                gradient ∇J(x, y):  the gradient of the objective function,
                                    i.e. the change for a specific theta θ
        """

        for key, value in changes_to_w.items():
            self.params[key] -= self.l_rate * value

    def compute_accuracy(self, x_val, y_val):
        """
            This function does a forward pass of x, then checks if the indices
            of the maximum value in the output equals the indices in the label
            y. Then it sums over each prediction and calculates the accuracy.
        """
        predictions = []

        for x, y in zip(x_val, y_val):
            output = self.forward_pass(x)
            pred = np.argmax(output)
            predictions.append(pred == np.argmax(y))

        return np.mean(predictions)

    def train(self, x_train, y_train, x_val, y_val):
        start_time = time.time()
        for iteration in range(self.epochs):
            for x, y in zip(x_train, y_train):
                output = self.forward_pass(x)
                changes_to_w = self.backward_pass(y, output)
                self.update_network_parameters(changes_to_w)

            accuracy = self.compute_accuracy(x_val, y_val)
            print('Epoch: {0}, Time Spent: {1:.2f}s, Accuracy: {2:.2f}%'.format(
                iteration + 1, time.time() - start_time, accuracy * 100
            ))

nn = NeuralNetwork(sizes=[42, 20, 12, numberofgestures])
nn.train(X_train, y_train, X_test, y_test)

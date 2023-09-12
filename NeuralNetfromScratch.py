import numpy as np
from sklearn.model_selection import train_test_split
import time

randomstate = 5 # is a random seed used for reproducibility.
dataset = "Model/gestures.csv" # csv file path
modelsavepath = "Model/model" # path of where to save model

numberofgestures = 5 # number of gestures to detect so the correct number of output nodes will be used
X_dataset = np.loadtxt(dataset, delimiter=',', dtype='float32', usecols=(range(1, 43))) # gestures.csv
# ^ loads the csv file text using only columns 2, 43. the np.loadtxt will load it into a numpy array
y_dataset = np.loadtxt(dataset, delimiter=',', dtype='int32', usecols=0) # gesture labels.csv
# ^ loads the corresponding labels from the first column in the dataset
X_train, X_test, y_train, y_test = train_test_split(X_dataset, y_dataset, train_size=0.75, random_state=randomstate) #




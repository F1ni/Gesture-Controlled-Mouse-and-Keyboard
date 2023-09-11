import numpy as np
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Input, Dropout, Dense
from sklearn.model_selection import train_test_split

randomstate = 5 # is a random seed used for reproducibility.
dataset = "Model/gestures.csv" # csv file path
modelsavepath = "Model/model" # path of where to save model

numberofgestures = 5 # number of gestures to detect so the correct number of output nodes will be used
X_dataset = np.loadtxt(dataset, delimiter=',', dtype='float32', usecols=(range(1, 43))) # gestures.csv
# ^ loads the csv file text using only columns 2, 43. the np.loadtxt will load it into a numpy array
y_dataset = np.loadtxt(dataset, delimiter=',', dtype='int32', usecols=0) # gesture labels.csv
# ^ loads the corresponding labels from the first column in the dataset
X_train, X_test, y_train, y_test = train_test_split(X_dataset, y_dataset, train_size=0.75, random_state=randomstate) #
# ^ the data is split into training data and testing data
# X_train, y_train is the training data and labels and the others contain the testing data.
# train size suggests that 75% of that data will be used for training

model = Sequential([
    Input(shape=(21 * 2, )),
    Dropout(0.2),
    Dense(20, activation='relu'),
    Dropout(0.4),
    Dense(12, activation='relu'),
    Dense(numberofgestures, activation='softmax')
])

# leeky-relu, change number of layers
# for model checkpointing - means saving the model weights and architecture
savingmodel = tf.keras.callbacks.ModelCheckpoint(modelsavepath, verbose=1, save_weights_only=False)
# for early stopping, which will stop training the data if the validation loss does not improve for a
# certain number of epochs - represented by patience
earlystopping = tf.keras.callbacks.EarlyStopping(patience=20, verbose=1)

# Model compilation
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)
# This compiles the model by specifying the optimization algorithm (adam),
# the loss function (sparse_categorical_crossentropy), and the evaluation metric (accuracy).

model.fit(
    X_train,
    y_train,
    epochs=1000,
    batch_size=4,
    validation_data=(X_test, y_test),
    callbacks=[savingmodel, earlystopping]
)
# fits the model to the training data. trains for 1000 epochs but has early stopping with batch size 4
# specifies the validation set for monitoring the models performance during training
#
# Loading the saved model
# test the data
# model = tf.keras.models.load_model(modelsavepath)
#
# # Model evaluation
# val_loss, val_acc = model.evaluate(X_test, y_test, batch_size=4)
# # Inference test
# predict_result = model.predict(np.array([X_test[0]]))
# print(np.squeeze(predict_result))
# print(np.argmax(np.squeeze(predict_result)))

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from sklearn.model_selection import train_test_split

randomstate = 5 # is a random seed used for reproducibility.
dataset = "Model/gestures.csv" # csv file path
modelsavepath = "Model/PytorchModel" # path of where to save model

numberofgestures = 5 # number of gestures to detect so the correct number of output nodes will be used
X_dataset = np.loadtxt(dataset, delimiter=',', dtype='float32', usecols=(range(1, 43))) # gestures.csv
# ^ loads the csv file text using only columns 2, 43. the np.loadtxt will load it into a numpy array
y_dataset = np.loadtxt(dataset, delimiter=',', dtype='int32', usecols=0) # gesture labels.csv
# ^ loads the corresponding labels from the first column in the dataset
X_train, X_test, y_train, y_test = train_test_split(X_dataset, y_dataset, train_size=0.75, random_state=randomstate)


class HandGestureRecognition(nn.Module):
    def __init__(self, input_size, HiddenLayer1, HiddenLayer2, outputlayer):
        super(HandGestureRecognition, self).__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_size, HiddenLayer1),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(HiddenLayer1, HiddenLayer2),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(HiddenLayer2, outputlayer),
            nn.Softmax(dim=1)
        )

    def forward(self, x):
        return self.layers(x)



inputsize = X_train.shape[1] # shape one gives the number of columns
sizeOfHiddenLayer1 = 20
sizeOfHiddenLayer2 = 12

model = HandGestureRecognition(inputsize, sizeOfHiddenLayer1, sizeOfHiddenLayer2, numberofgestures)
lossfunction = nn.CrossEntropyLoss() # instance for the cross entropy
optimiser = optim.Adam(model.parameters(), lr=0.001) # instance for the adam optimiser

# for training the data
epochs = 1000
batch_size = 4
patience = 20
best_val_loss = float('inf')
no_improvement = 0

for epoch in range(epochs):
    for i in range(0, X_train.shape[0], batch_size): # .shape[0] gives the number of rows in the array. #
        # the batch size means it will make i every 4th
        end = i + batch_size
        X_batch = torch.tensor(X_train[i:end], dtype=torch.float32)
        y_batch = torch.tensor(y_train[i:end], dtype=torch.long)

        optimiser.zero_grad()
        outputs = model(X_batch)
        loss = lossfunction(outputs, y_batch)
        loss.backward()
        optimiser.step()
        # Validation
        with torch.no_grad():
            X_val = torch.tensor(X_test, dtype=torch.float32)
            y_val = torch.tensor(y_test, dtype=torch.long)
            val_outputs = model(X_val)
            val_loss = lossfunction(val_outputs, y_val).item()

        print(f"Epoch {epoch + 1}/{epochs} - Loss: {loss:.4f} - Validation Loss: {val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            no_improvement = 0
            torch.save(model.state_dict(), modelsavepath)
        else:
            no_improvement += 1

        if no_improvement >= patience:
            print(f"Early stopping at epoch {epoch + 1}")
            break

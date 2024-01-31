import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from sklearn.model_selection import train_test_split

# Set random seed for reproducibility
torch.manual_seed(5)

# Load dataset
dataset_path = "Model/gestures.csv"
number_of_gestures = 4

X_dataset = np.loadtxt(dataset_path, delimiter=',', dtype='float32', usecols=(range(1, 43)))
y_dataset = np.loadtxt(dataset_path, delimiter=',', dtype='int64', usecols=0)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_dataset, y_dataset, train_size=0.75, random_state=5)

# Convert data to PyTorch tensors
X_train = torch.tensor(X_train)
y_train = torch.tensor(y_train, dtype=torch.long)
X_test = torch.tensor(X_test)
y_test = torch.tensor(y_test, dtype=torch.long)

# Create a PyTorch model
class GestureModel(nn.Module):
    def __init__(self, input_size, num_classes):
        super(GestureModel, self).__init__()
        self.fc1 = nn.Linear(input_size, 22)
        self.dropout1 = nn.Dropout(0.2)
        self.fc2 = nn.Linear(22, 9)
        self.dropout2 = nn.Dropout(0.4)
        self.fc3 = nn.Linear(9, num_classes)

    def forward(self, x):
        x = torch.relu(self.dropout1(self.fc1(x)))
        x = torch.relu(self.dropout2(self.fc2(x)))
        x = torch.softmax(self.fc3(x), dim=1)
        return x

# model = GestureModel(input_size=21 * 2, num_classes=number_of_gestures)
#
# # Set device and move model to device (GPU if available)
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model.to(device)
#
# # Loss function and optimizer
# criterion = nn.CrossEntropyLoss()
# optimizer = optim.Adam(model.parameters())
#
# # Training loop
# epochs = 1000
# batch_size = 4
#
# val_losses = []  # Initialize val_losses list
#
# for epoch in range(epochs):
#     # Training
#     model.train()
#     optimizer.zero_grad()
#     outputs = model(X_train.float().to(device))
#     loss = criterion(outputs, y_train.to(device))
#     loss.backward()
#     optimizer.step()
#
#     # Validation
#     model.eval()
#     with torch.no_grad():
#         val_outputs = model(X_test.float().to(device))
#         val_loss = criterion(val_outputs, y_test.to(device))
#
#     # Print and save logs
#     print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item()}, Val Loss: {val_loss.item()}")
#
#     # Early stopping
#     if epoch > 20 and val_loss >= min(val_losses[-20:]):
#         print("Early stopping.")
#         break
#
#     val_losses.append(val_loss.item())  # Append val_loss to val_losses list
#
# # Save the trained model only if early stopping is not triggered
# if epoch <= 1000:
#     model_save_path = "model.pth"
#     torch.save(model.state_dict(), model_save_path)
#     print(f"Model saved to {model_save_path}")

# is it cos i created the directory on the laptop instead of the computer? - no it wasnt
# it was because it needed to be in the file model.pth

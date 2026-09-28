"""Architecture of the bundled four-class PyTorch gesture model.

Training intentionally lives outside this module so importing the application
cannot retrain or overwrite the released weights.
"""

import torch
from torch import nn


class GestureModel(nn.Module):
    def __init__(self, input_size: int = 42, num_classes: int = 4) -> None:
        super().__init__()
        self.fc1 = nn.Linear(input_size, 22)
        self.dropout1 = nn.Dropout(0.2)
        self.fc2 = nn.Linear(22, 9)
        self.dropout2 = nn.Dropout(0.4)
        self.fc3 = nn.Linear(9, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = torch.relu(self.dropout1(self.fc1(x)))
        x = torch.relu(self.dropout2(self.fc2(x)))
        return torch.softmax(self.fc3(x), dim=1)

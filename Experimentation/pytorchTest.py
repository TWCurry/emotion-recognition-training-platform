# Test script to experiment with pytorch
import torch

x = torch.ones(2, 2, requires_grad=True)
y = x +2
print(y)
# REFERENCE: https://github.com/christiancosgrove/pytorch-spectral-normalization-gan/blob/master/main.py
# Generic import
import argparse

# PyTorch import
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms

# Custom import
import model
import train
from res_net import *

parser = argparse.ArgumentParser()
parser.add_argument('--batch_size', type = int, default = 64)
parser.add_argument('--lr', type = float, default = 1e-3)
parser.add_argument('--checkpoint_dir', type = str, default = '../checkpoints')

args = parser.parse_args()

# Load CIFAR data
loader = torch.utils.data.DataLoader(
            datasets.CIFAR10('../data', train = True, download = True,
                transform = transforms.Compose([
                    transforms.ToTensor(),
                    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])),
                batch_size = args.batch_size, shuffle = True, num_workers = 1)

# Controlling variables
z_dim = 128
dis_iterations = 2
num_epochs = 100

generator = model.Generator(z_dim)
discriminator = model.Discriminator()

generator = train.get_cuda(generator)
discriminator = train.get_cuda(discriminator)

gen_optimizer = optim.Adam(generator.parameters(), lr = 2e-5, betas = (0.0, 0.999))
dis_optimizer = optim.Adam(discriminator.parameters(), lr = 5e-5, betas = (0.0, 0.999))

train.train(generator, discriminator, gen_optimizer, dis_optimizer, loader, dis_iterations,
            batch_size = args.batch_size, num_epochs = num_epochs)

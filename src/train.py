# Generic import
import os
# PyTorch import
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision as tv

# Custom import
import utils
import model
from res_net import *

IS_CUDA = False
def get_cuda(x):
    if torch.cuda.is_available():
        return x.cuda()
    return x

def evaluate(generator, discriminator, x, epoch, output_dir = './output/'):
    samples = generator(x)
    file_name = output_dir + 'Epoch_{}.jpg'.format(epoch)
    utils.save_image(samples, file_name)

def train(generator, discriminator, gen_optimizer, dis_optimizer,
          data_loader, dis_iterations = 2, batch_size = 32, num_epochs = 10,
          z_dim = 128, checkpoints_dir = '../checkpoints'):
    # print('Generator', generator)
    # print('Discriminator', discriminator)

    # Exponentially Decaying learning rate
    exp_lr_d = optim.lr_scheduler.ExponentialLR(dis_optimizer, gamma=0.99)
    exp_lr_g = optim.lr_scheduler.ExponentialLR(gen_optimizer, gamma=0.99)

    fixed_x = get_cuda(torch.randn(batch_size, z_dim))

    model_dir = checkpoints_dir+'/saved_models/'
    output_dir = checkpoints_dir+'/output/'
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    for epoch in range(1, num_epochs+1):
        total_dis_loss = 0
        total_gen_loss = 0
        for batch_idx, (data, target) in enumerate(data_loader):
            if data.size()[0] != batch_size:
                continue
            data = get_cuda(data)
            target = get_cuda(target)

            for _ in range(dis_iterations):
                z = get_cuda(torch.randn(batch_size, z_dim))

                gen_optimizer.zero_grad()
                dis_optimizer.zero_grad()

                dis_loss = - discriminator(data).mean() + discriminator(generator(z)).mean()

                dis_loss.backward()
                dis_optimizer.step()

            z = get_cuda(torch.randn(batch_size, z_dim))

            # Train generator
            gen_optimizer.zero_grad()
            dis_optimizer.zero_grad()

            gen_loss = -discriminator(generator(z)).mean()
            gen_loss.backward()
            gen_optimizer.step()

            total_dis_loss += dis_loss
            total_gen_loss += gen_loss
            if batch_idx % 100 == 0:
                print('Loss: Generator = ', gen_loss.item(), ' Discriminator = ', dis_loss.item())
                evaluate(generator, discriminator, fixed_x, epoch, output_dir = output_dir)
        exp_lr_d.step()
        exp_lr_g.step()
        print('Epoch {}'.format(epoch), ' Loss: Generator = ', total_gen_loss.item(), ' Discriminator = ', total_dis_loss.item())
        evaluate(generator, discriminator, fixed_x, epoch, output_dir = output_dir)
        if epoch % 5 == 0:
            torch.save(discriminator.state_dict(), os.path.join(model_dir), 'dis_{}'.format(epoch / 5))
            torch.save(generator.state_dict(), os.path.join(model_dir), 'gen_{}'.format(epoch / 5))

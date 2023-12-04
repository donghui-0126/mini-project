# https://github.com/seungeunrho/minimalRL

#PPO-LSTM
import gym
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Categorical
import time
import numpy as np

#Hyperparameters
learning_rate = 0.0005
gamma         = 0.98
lmbda         = 0.99
eps_clip      = 0.01
K_epoch       = 10


class PPO(nn.Module):
    def __init__(self):
        super(PPO, self).__init__()
        self.data = []

        self.fc1 = nn.Linear(122, 128)
        
        self.lstm1 = nn.LSTM(128, 64)
        self.lstm2 = nn.LSTM(64, 64)

        self.fc_pi1 = nn.Linear(64, 32)
        self.fc_pi2 = nn.Linear(32, 16)
        self.fc_pi3 = nn.Linear(16, 11)

        self.fc_v1 = nn.Linear(64, 32)
        self.fc_v2 = nn.Linear(32, 8)
        self.fc_v3 = nn.Linear(8, 1)

        self.optimizer = optim.Adam(self.parameters(), lr=learning_rate)

    def pi(self, x, hidden1, hidden2):
        x = F.relu(self.fc1(x))
        x = x.view(-1, 1, 128)
        x, lstm_hidden1 = self.lstm1(x, hidden1)
        x, lstm_hidden2 = self.lstm2(x, hidden2)
        
        x = F.relu(self.fc_pi1(x))
        x = F.relu(self.fc_pi2(x))

        prob = F.softmax(self.fc_pi3(x), dim=2)

        return prob, lstm_hidden1, lstm_hidden2 

    def v(self, x, hidden1, hidden2):
        x = F.relu(self.fc1(x))
        x = x.view(-1, 1, 128)
        x, lstm_hidden1 = self.lstm1(x, hidden1)
        x, lstm_hidden2 = self.lstm2(x, hidden2)
        
        x = F.relu(self.fc_v1(x))
        x = F.relu(self.fc_v2(x))

        v = self.fc_v3(x)

        return v

    def put_data(self, transition):
        self.data.append(transition)

    def make_batch(self):
        s_lst, a_lst, r_lst, s_prime_lst, prob_a_lst, h1_in_lst, h1_out_lst, h2_in_lst, h2_out_lst, done_lst = \
            [], [], [], [], [], [], [], [], [], []


        for transition in self.data:
            s, a, r, s_prime, prob_a, h1_in, h1_out, h2_in, h2_out, done = transition
            s_lst.append(s)
            a_lst.append([a])
            r_lst.append([r])
            s_prime_lst.append(s_prime)
            prob_a_lst.append([prob_a])
            h1_in_lst.append(h1_in)
            h1_out_lst.append(h1_out)
            h2_in_lst.append(h2_in)
            h2_out_lst.append(h2_out)
            done_mask = 0 if done else 1
            done_lst.append([done_mask])

        s, a, r, s_prime, done_mask, prob_a = torch.tensor(s_lst, dtype=torch.float), torch.tensor(a_lst), \
                                         torch.tensor(r_lst), torch.tensor(s_prime_lst, dtype=torch.float), \
                                         torch.tensor(done_lst, dtype=torch.float), torch.tensor(prob_a_lst, dtype=torch.float)
        self.data = []
        return s,a,r,s_prime, done_mask, prob_a, h1_in_lst[0], h1_out_lst[0], h2_in_lst[0], h2_out_lst[0]

    def train_net(self):
        s,a,r,s_prime,done_mask, prob_a, (h1_in_1, h1_in_2), (h1_out_1, h1_out_2), (h2_in_1, h2_in_2), (h2_out_1, h2_out_2) = \
            self.make_batch()
        first_hidden1  = (h1_in_1.detach(), h1_in_2.detach())
        second_hidden1 = (h1_out_1.detach(), h1_out_2.detach())

        first_hidden2  = (h2_in_1.detach(), h2_in_2.detach())
        second_hidden2 = (h2_out_1.detach(), h2_out_2.detach())

        for i in range(K_epoch):
            v_prime = self.v(s_prime, second_hidden1, second_hidden2).squeeze(1)
            td_target = r + gamma * v_prime * done_mask
            v_s = self.v(s, first_hidden1, first_hidden2).squeeze(1)
            delta = td_target - v_s
            delta = delta.detach().numpy()

            advantage_lst = []
            advantage = 0.0
            for item in delta[::-1]:
                advantage = gamma * lmbda * advantage + item[0]
                advantage_lst.append([advantage])
            advantage_lst.reverse()
            advantage = torch.tensor(advantage_lst, dtype=torch.float)



            pi, _, __ = self.pi(s, first_hidden1, first_hidden2) 
            pi_a = pi.squeeze(1).gather(1,a)
            ratio = torch.exp(torch.log(pi_a) - torch.log(prob_a))  # a/b == log(exp(a)-exp(b))

            surr1 = ratio * advantage
            surr2 = torch.clamp(ratio, 1-eps_clip, 1+eps_clip) * advantage
            loss = -torch.min(surr1, surr2) + F.smooth_l1_loss(v_s, td_target.detach())

            self.optimizer.zero_grad()
            loss.mean().backward(retain_graph=True)
            self.optimizer.step()
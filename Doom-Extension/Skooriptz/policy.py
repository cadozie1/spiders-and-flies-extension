import torch.functional as F
import torch.nn as nn
import torch
import random
import numpy as np

#policy gradient nn taken and adapted from https://huggingface.co/deep-rl-course/unit4/hands-on?fw=pt
class Policy(torch.nn.Module):
    def __init__(self, s_size, a_size, h_size):
        super(Policy, self).__init__()
        self.fc1 = nn.Linear(s_size, h_size)
        self.fc2 = nn.Linear(h_size, a_size)

    def forward(self, x):
        x = nn.functional.relu(self.fc1(x))
        x = self.fc2(x)
        return nn.functional.softmax(x, dim=1)

    def act(self, explore, state):
        #determine whether to explore or exploit
        exp = random.choices([0, 1], weights=[explore, (1-explore)], k=1)


        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        state = torch.from_numpy(state).float().unsqueeze(0).to(device)
        probs = self.forward(state).cpu()
        #explore, so choose from equal weights
        if exp[0] == 0:
            action = random.choice([0, 1, 2, 3, 4, 5])
            action_prob = probs.detach().numpy()[0][action]
            action_prob_arr = np.array([action_prob], dtype=np.float32)
            action_log_prob = torch.log(torch.from_numpy(action_prob_arr))
            return action, action_log_prob
        m = torch.distributions.Categorical(probs)
        action = m.sample()
        return action.item(), m.log_prob(action) 

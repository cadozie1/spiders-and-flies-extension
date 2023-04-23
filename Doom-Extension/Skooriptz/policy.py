import torch


#policy gradient nn taken from https://huggingface.co/deep-rl-course/unit4/hands-on?fw=pt
class Policy(torch.nn.Module):
    def __init__(self, s_size, a_size, h_size):
        super(Policy, self).__init__()
        self.fc1 = torch.nn.Linear(s_size, h_size)
        self.fc2 = torch.nn.Linear(h_size, a_size)

    def forward(self, x):
        x = torch.nn.functional.relu(self.fc1(x))
        x = self.fc2(x)
        return torch.nn.functional.softmax(x, dim=1)

    def act(self, state):
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        state = torch.from_numpy(state).float().unsqueeze(0).to(device)
        probs = self.forward(state).cpu()
        m = torch.distributions.Categorical(probs)
        action = m.sample()
        return action.item(), m.log_prob(action)

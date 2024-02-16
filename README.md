# spiders-and-flies-extension

## Description
In this project, we compare ordinary and multiagent rollout to optimize the number of moves for spiders to eat flies on a grid. We provide multiple commandline customizations including varying grid sizes, varying spider and fly quantities, varying fly policies, and varying initial positions. The visualization is performed using PyTorch and enables the user to create console output, picture drawings of the iterations, or even GIFs.

Additionally, we attempt to adapt multiagent rollout to DOOM, but found the dynamic environment to be much more difficult to navigate.

## Results
Overall, multiagent rollout does perform with comparable accuracy to ordinary rollout with major computational improvement.

![](https://github.com/cadozie1/spiders-and-flies-extension/blob/main/courtney_code/animation.gif)

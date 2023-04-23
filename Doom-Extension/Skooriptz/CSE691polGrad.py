#!/usr/bin/env python3

#####################################################################
# This script presents how to use the most basic features of the environment.
# It configures the engine, and makes the agent perform random actions.
# It also gets current state and reward earned with the action.
# <episodes> number of episodes are played. 
# Random combination of buttons is chosen for every action.
# Game variables from state and last reward are printed.
#
# To see the scenario description go to "../../scenarios/README.md"
#####################################################################

import os
import numpy as np
from random import choice
from time import sleep
import vizdoom as vzd
import torch
import policy 
from collections import deque

#policy gradient taken and adapted from https://huggingface.co/deep-rl-course/unit4/hands-on?fw=pt
def reinforce(game, policy, optimizer, n_training_episodes, max_t, gamma):
    scores_deque = deque(maxlen=100)
    scores = []
    actions = [[True, False, False, False, False, False], [False, True, False, False, False, False], [False, False, True, False, False, False], [False, False, False, True, False, False], [False, False, False, False, True, False], [False, False, False, False, False, True]]
    #exploration probability value - start high & compound so we start off exploring more
    explore = 0.9

    sleep_time = 1.0 / vzd.DEFAULT_TICRATE  # = 0.028
    for i in range(n_training_episodes):

        saved_log_probs = []
        rewards = []

        print("Episode #" + str(i + 1))

        # Starts a new episode. It is not needed right after init() but it doesn't cost much. At least the loop is nicer.
        game.new_episode() 

        t = 0
        while not game.is_episode_finished():
            if t >= max_t:
                break

            # Gets the state
            state = game.get_state()

            # Which consists of:
            n = state.number
            vars = state.game_variables
            screen_buf = state.screen_buffer
            depth_buf = state.depth_buffer
            labels_buf = state.labels_buffer
            automap_buf = state.automap_buffer
            labels = state.labels
            objects = state.objects
            sectors = state.sectors

            # Games variables can be also accessed via
            # (including the ones that were not added as available to a game state):
            #game.get_game_variable(GameVariable.AMMO2)

            # Makes an action (here random one) and returns a reward.
            action, log_prob = policy.act((explore), state.game_variables)
            #if we explore, can't easily save the probability -> log_prob = 0
            if log_prob != 0:
                saved_log_probs.append(log_prob)

            r = game.make_action(actions[action])
            rewards.append(r)

            # Makes a "prolonged" action and skip frames:
            # skiprate = 4
            # r = game.make_action(choice(actions), skiprate)

            # The same could be achieved with:
            # game.set_action(choice(actions))
            # game.advance_action(skiprate)
            # r = game.get_last_reward()

            # Prints state's game variables and reward.
            print("State #" + str(n))
            print("Game variables:", vars)
            print("Reward:", r)
            print("=====================")

            t += 1
            if sleep_time > 0:
                sleep(sleep_time)

            explore *= 0.9999

        

        scores_deque.append(sum(rewards))
        scores.append(sum(rewards))
        returns = deque(maxlen=max_t)
        n_steps = len(rewards)

        for t in range(n_steps)[::-1]:
            disc_return_t = returns[0] if len(returns) > 0 else 0
            returns.appendleft(gamma * disc_return_t + rewards[t])

        ## standardization of the returns is employed to make training more stable
        eps = np.finfo(np.float32).eps.item()
        ## eps is the smallest representable float, which is
        # added to the standard deviation of the returns to avoid numerical instabilities
        returns = torch.tensor(returns)
        returns = (returns - returns.mean()) / (returns.std() + eps)

        # Line 7:
        policy_loss = []
        for log_prob, disc_return in zip(saved_log_probs, returns):
            policy_loss.append(-log_prob * disc_return)
        policy_loss = torch.cat(policy_loss).sum()

        # Line 8: PyTorch prefers gradient descent
        optimizer.zero_grad()
        policy_loss.backward()
        optimizer.step()


        # Check how the episode went.
        print("Episode finished.")
        print("Total reward:", game.get_total_reward())
        print("Average Score: {:.2f}".format(i, np.mean(scores_deque)))
        print("************************")
    # It will be done automatically anyway but sometimes you need to do it in the middle of the program...

    return scores

def evaluate_agent(game, n_eval_episodes, policy):
    """
    Evaluate the agent for ``n_eval_episodes`` episodes and returns average reward and std of reward.
    :param n_eval_episodes: Number of episode to evaluate the agent
    :param policy: The Reinforce agent
    """
    actions = [[True, False, False, False, False, False], [False, True, False, False, False, False], [False, False, True, False, False, False], [False, False, False, True, False, False], [False, False, False, False, True, False], [False, False, False, False, False, True]]

    sleep_time = 1.0 / vzd.DEFAULT_TICRATE  # = 0.028
    episode_rewards = []
    for i in range(n_eval_episodes):
        total_rewards_ep = 0
        print("Episode #" + str(i + 1))

        # Starts a new episode. It is not needed right after init() but it doesn't cost much. At least the loop is nicer.
        game.new_episode() 

        while not game.is_episode_finished():

            # Gets the state
            state = game.get_state()

            # Which consists of:
            n = state.number
            vars = state.game_variables
            screen_buf = state.screen_buffer
            depth_buf = state.depth_buffer
            labels_buf = state.labels_buffer
            automap_buf = state.automap_buffer
            labels = state.labels
            objects = state.objects
            sectors = state.sectors


            #we're testing, so don't explore any - explore=0
            action, _ = policy.act(0.1, state.game_variables)
            r = game.make_action(actions[action])
            total_rewards_ep += r

            if sleep_time > 0:
                sleep(sleep_time)


        episode_rewards.append(total_rewards_ep)
    mean_reward = np.mean(episode_rewards)
    std_reward = np.std(episode_rewards)

    return mean_reward, std_reward

if __name__ == "__main__":
    # Create DoomGame instance. It will run the game and communicate with you.
    game = vzd.DoomGame()

    # Now it's time for configuration!
    # load_config could be used to load configuration instead of doing it here with code.
    # If load_config is used in-code configuration will also work - most recent changes will add to previous ones.
    game.load_config("CSE691.cfg")

    # Sets path to additional resources wad file which is basically your scenario wad.
    # If not specified default maps will be used and it's pretty much useless... unless you want to play good old Doom.
    game.set_doom_scenario_path(os.path.join(vzd.scenarios_path, "/home/quartz/spiders-and-flies-extension-main/Doom-Extension/Skooriptz/CSE691.wad"))

    # Sets map to start (scenario .wad files can contain many maps).
    game.set_doom_map("map01")

    # Sets resolution. Default is 320X240
    game.set_screen_resolution(vzd.ScreenResolution.RES_640X480)

    # Sets the screen buffer format. Not used here but now you can change it. Default is CRCGCB.
    game.set_screen_format(vzd.ScreenFormat.RGB24)

    # Enables depth buffer.
    game.set_depth_buffer_enabled(True)

    # Enables labeling of in game objects labeling.
    game.set_labels_buffer_enabled(True)

    # Enables buffer with top down map of the current episode/level.
    game.set_automap_buffer_enabled(True)

    # Enables information about all objects present in the current episode/level.
    game.set_objects_info_enabled(True)

    # Enables information about all sectors (map layout).
    game.set_sectors_info_enabled(True)

    game.set_available_buttons([vzd.Button.TURN_LEFT, vzd.Button.TURN_RIGHT, vzd.Button.MOVE_FORWARD, vzd.Button.MOVE_LEFT, vzd.Button.MOVE_RIGHT, vzd.Button.ATTACK])
    # Buttons that will be used can be also checked by:
    print("Available buttons:", [b.name for b in game.get_available_buttons()])

    # Adds game variables that will be included in state.
    # Similarly to buttons, they can be added one by one:
    # game.clear_available_game_variables()
    # game.add_available_game_variable(vzd.GameVariable.AMMO2)
    # Or:
    game.set_available_game_variables([vzd.GameVariable.AMMO2, vzd.GameVariable.SELECTED_WEAPON, vzd.GameVariable.KILLCOUNT, vzd.GameVariable.HITCOUNT, vzd.GameVariable.HITS_TAKEN, vzd.GameVariable.DAMAGECOUNT, vzd.GameVariable.DAMAGE_TAKEN, vzd.GameVariable.HEALTH, vzd.GameVariable.DEAD, vzd.GameVariable.POSITION_Y, vzd.GameVariable.POSITION_Z])
    print("Available game variables:", [v.name for v in game.get_available_game_variables()])

    # Causes episodes to finish after 200 tics (actions)
    game.set_episode_timeout(200)

    # Makes episodes start after 10 tics (~after raising the weapon)
    game.set_episode_start_time(10)

    # Makes the window appear (turned on by default)
    game.set_window_visible(True)

    #game.set_sound_enabled(True)
    # Because of some problems with OpenAL on Ubuntu 20.04, we keep this line commented,
    # the sound is only useful for humans watching the game.

    # Sets the living reward (for each move) to -1
    #game.set_living_reward(-1)

    # Sets ViZDoom mode (PLAYER, ASYNC_PLAYER, SPECTATOR, ASYNC_SPECTATOR, PLAYER mode is default)
    game.set_mode(vzd.Mode.PLAYER)

    # Enables engine output to console, in case of a problem this might provide additional information.
    game.set_console_enabled(True)

    # Initialize the game. Further configuration won't take any effect from now on.
    game.init()

    # Run this many episodes
    episodes = 1

    actions = [[True, False, False, False, False, False], [False, True, False, False, False, False], [False, False, True, False, False, False], [False, False, False, True, False, False], [False, False, False, False, True, False], [False, False, False, False, False, True]]

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    hyperparameters = {
            "h_size": 50,
            "n_training_episodes": 20,
            "n_evaluation_episodes": 10,
            "max_t": 200,
            "gamma": 1.0,
            "lr": 1e-2,
            "state_space": 11,
            "action_space": 6,
            }
    doom_policy = policy.Policy(
            hyperparameters["state_space"],
            hyperparameters["action_space"],
            hyperparameters["h_size"],
            ).to(device)
    optimizer = torch.optim.Adam(doom_policy.parameters(), lr=hyperparameters["lr"])


    scores = reinforce(game, doom_policy, optimizer, hyperparameters["n_training_episodes"], hyperparameters["max_t"], hyperparameters["gamma"],) 

    mean_reward, std_reward = evaluate_agent(game, 
    hyperparameters["n_evaluation_episodes"], doom_policy 
    )
    print("Mean reward: ", mean_reward, "Standard Deviation: ", std_reward)

    game.close()


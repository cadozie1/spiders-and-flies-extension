import os
import numpy as np
from random import choice
from time import sleep
import vizdoom as vzd
import torch
import policy
from collections import deque
import pickle


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

def start_game(window_visible):
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
    game.set_window_visible(window_visible)

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

    return game


if __name__ == "__main__":
    game = start_game(True)
    with open("trained_policy.pkl", "rb") as file:
        doom_policy = pickle.load(file)
    
    n_evaluation_episodes = 15
    mean_reward, std_reward = evaluate_agent(game, 
    n_evaluation_episodes, doom_policy 
    )
    print("Mean reward: ", mean_reward, "Standard Deviation: ", std_reward)

    game.close()


#!/usr/bin/env python3

#####################################################################
# This script demonstrates game save and load functionality.
#####################################################################

# WARNING:
# Please note that this feature is experimental and not well tested!

import itertools as it
import os
from random import choice
from random import randrange
from time import sleep
import vizdoom as vzd

if __name__ == "__main__":
    # Create DoomGame instance. It will run the game and communicate with you.
    game = vzd.DoomGame()
    game.load_config("Final.cfg")
    game.set_doom_scenario_path("Final.wad")
    #game.set_render_hud(True)
    game.set_objects_info_enabled(True)
    game.set_window_visible(False)

    game.add_available_game_variable(vzd.GameVariable.POSITION_X)
    game.add_available_game_variable(vzd.GameVariable.POSITION_Y)

    # Creates all possible actions depending on how many buttons there are.
    actions_num = game.get_available_buttons_size()
    actions = [[True, False, False, False, False], [False, True, False, False, False], [False, False, True, False, False], [False, False, False, True, False], [False, False, False, False, True]]


    game.set_window_visible(True)
    game.set_mode(vzd.Mode.PLAYER)
    #game.set_mode(vzd.Mode.ASYNC_PLAYER)
    #game.set_ticrate(35)
    game.init()


    # Sets time that will pause the engine after each action (in seconds)
    # Without this everything would go too fast for you to keep track of what's happening.
    sleep_time = 1.0 / vzd.DEFAULT_TICRATE  # = 0.028


    def Manhattan_Action(game):
    # Get current state
        # Find next action
        game.save("save3.png")
        best_dist = float('inf')
        best_act2 = None
        for z in range(actions_num):
            game.new_episode
            game.load("save3.png")
            game.make_action(actions[z],1)
            state = game.get_state()
            if state == None:
                if best_act2 == None:
                    return actions[z]
                else:
                    return best_act2
            objects = state.objects
            for k in objects:
                if k.name == "GreenArmor":
                    armor = k
                elif k.name == "DoomPlayer":
                    player = k
            yA = armor.position_y
            xA = armor.position_x
            yP = player.position_y
            xP = player.position_x
            dist = abs(yA - yP) + abs(xA - xP)
            if abs(dist) < best_dist:
                best_dist = abs(dist)
                best_act2 = actions[i]

        return best_act2



    print("Starting Episode")

    # Starts a new episode.
    current_reward = 0
    action_limit = 500
    action_count = 0
    game.new_episode()
    action_list = []
    while action_count < action_limit and not game.is_episode_finished():
        game.save("save.png")
        print("\nGame saved!")
        best_reward = float('-inf')
        best_action = None
        for i in range(actions_num):
            game.new_episode()
            game.load("save.png")
            game.make_action(actions[i])
            reward = 0
            action_limit2 = 10
            action_count2 = 0
            while action_count2 < action_limit2 and not game.is_episode_finished():
                # Time to construct our state.
                state = game.get_state()
                game.save("save2.png")
                for j in range(actions_num):
                    game.new_episode()
                    game.load("save2.png")
                    epsilon = randrange(1,101)
                    if epsilon <= 15:
                        action = choice(actions)
                    else:
                        action = Manhattan_Action(game)
                game.new_episode()
                game.load("save2.png")
                reward = reward + game.make_action(action)
                fixed_shaping_reward = game.get_game_variable(vzd.GameVariable.USER1)
                shaping_reward = vzd.doom_fixed_to_double(
                fixed_shaping_reward)
                action_count2 = action_count2 + 1
            print("The total reward for this action is: " + str(reward))
            if reward+shaping_reward > best_reward:
                best_reward = reward+shaping_reward
                best_action = actions[i]
        game.new_episode()
        game.load("save.png")
        print(best_action)
        current_reward = current_reward + game.make_action(best_action)
        print(current_reward)
        action_count = action_count + 1
        action_list.append(best_action)



    
    game.close()
    #Now let's watch it
    print("Best Reward: " + str(current_reward))

    # Delete save file
    os.remove("save.png")
    os.remove("save2.png")
    os.remove("save3.png")

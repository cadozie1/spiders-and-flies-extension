import sys, argparse
import image_grid
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
import shutil
import random
from enum import Enum

#an enum that defines each of the actions a spider can take
Action = Enum('Action', ['UP', 'DOWN', 'LEFT', 'RIGHT', 'STILL'])

#print the lists of game states to the console
def print_output(FS_list):
    for i in range(0, len(FS_list)):
        
        flies, spiders = FS_list[i]
        print("Game state", i)
        print("Flies: ", flies)
        print("Spiders: ", spiders, "\n")
    
    

#a function that animates a list of game states and returns in GIF format for a given filename
#can easily change to mp4 tho
def plot_animate(FS_list, gridsize, filename):

    fig, axs = plt.subplots(figsize=(6, 6))
    im = axs.imshow(image_grid.grid(FS_list[0], gridsize), extent=[0, gridsize[0], gridsize[1], 0])


    def animate_func(i):
        im.set_array(image_grid.grid(FS_list[i], gridsize))
        return [im]
    anim = animation.FuncAnimation(
                                    fig,
                                    animate_func,
                                    frames = len(FS_list),
                                    interval = 500,
                                    )
    anim.save(filename + '.gif')


#a function that plots a series of game states as a bunch of images in a specified folder
def plot_images(FS_list, gridsize, file_folder):
    if os.path.exists(file_folder) and os.path.isdir(file_folder):
        shutil.rmtree(file_folder)
    os.mkdir(file_folder)
    for i in range(0, len(FS_list)):
        fig, axs = plt.subplots(figsize=(6, 6))
        im = axs.imshow(image_grid.grid(FS_list[i], gridsize), extent=[0, gridsize[0], gridsize[1], 0])
        plt.savefig(str(file_folder + '/anim' + str(i)))
        
#a function that returns the manhattan distance between 2 pairs of coordinates
def manhattan_distance(coordinates1, coordinates2):
    return abs(coordinates1[0]-coordinates2[0]) + abs(coordinates1[1] - coordinates2[1])

#a function that returns the horizontal distance between 2 pairs of coordinates
def manhattan_x(coordinates1, coordinates2):
    return abs(coordinates1[0]-coordinates2[0])

#a function that moves a given spider/fly at a given index by a certain action and updates the FS gamestate
# isASpider: True -> move a spider; False -> move a fly
def move(FS, action, isASpider, index):
    new_FS = []
    moving_list = [] #the list of spiders/flies for the spider/fly we're moving
    if isASpider == True:
        new_FS.append(list(FS[0])) #keep flies same if we're just moving a spider
        moving_list = list(FS[1]) #start with same spiders, but going to change one
    else:
        moving_list = list(FS[0]) # start with same flies, but going to change one


    #assume we check for or know legality of action before calling this function :)
    if (action == Action.UP):
        old_coords = moving_list[index]
        new_coords = (old_coords[0], old_coords[1] - 1)
    elif (action == Action.DOWN):
        old_coords = moving_list[index]
        new_coords = (old_coords[0], old_coords[1] + 1)
    elif (action == Action.LEFT):
        old_coords = moving_list[index]
        new_coords = (old_coords[0] - 1, old_coords[1])
    elif (action == Action.RIGHT):
        old_coords = moving_list[index]
        new_coords = (old_coords[0] + 1, old_coords[1])
    elif (action == Action.STILL):
        new_coords = moving_list[index]

    moving_list[index] = new_coords

    new_FS.append(moving_list)

    if isASpider == False:
        new_FS.append(list(FS[1])) #keep spiders same if we're just moving a fly
        #if spider eats a fly, get rid of fly
        for spider in FS[1]:
            if new_coords == spider:
                new_FS[0].remove(new_coords)

    else:
        #if spider eats a fly, get rid of fly
        for fly in FS[0]:
            if new_coords == fly:
                new_FS[0].remove(fly)

    return new_FS

#a function that determines and prioritizes the legal actions for a given spider at specified coordinates
def legal_actions(coords, gridsize):
    x, y = coords
    legals = []
    #give preference to still, then horizontal actions, then vertical in list of actions
    # (as tiebreakers will be given to first action in the list and we'd rather the spiders move as minimal as possible - more still actions)
    legals.append(Action.STILL)
    if x > 0:
        legals.append(Action.LEFT)
    if x < gridsize[0]-1:
        legals.append(Action.RIGHT)
    if y > 0:
        legals.append(Action.UP)
    if y < gridsize[1]-1:
        legals.append(Action.DOWN)

    return legals


#a function that returns what action a given spider at a given spiderIndex would perform based on the base policy for a given gamestate FS
def base_policy_spider(FS, gridsize, spiderIndex):
    flies, spiders = FS
    spider = spiders[spiderIndex]

    #get legal actions
    if len(flies) == 0: return None 
    actions = legal_actions(spider, gridsize)
    closest_fly = flies[0]
    min_dist = manhattan_distance(spider, flies[0])
    for fly in flies[1:]:
        dist = manhattan_distance(spider, fly)
        if dist < min_dist:
            min_dist = dist
            closest_fly = fly
        #tiebreaker is horizontal distance
        elif min_dist == dist:
            #determine which is more horizontal
            if manhattan_x(spider, fly) < manhattan_x(spider, closest_fly):
                min_dist = dist
                closest_fly = fly
    best_action = None
    if (spider[0] - closest_fly[0]) > 0:
        best_action = Action.LEFT
    elif (spider[0] - closest_fly[0]) < 0:
        best_action = Action.RIGHT
    else:
        if (spider[1] - closest_fly[1]) > 0:
            best_action = Action.UP
        elif (spider[1] - closest_fly[1]) < 0:
            best_action = Action.DOWN
    return best_action 
    
    
#a function that returns the updated list of gamestates FS_list and number of moves thus far that have been done for the base policy, adding on one move for each spider to the list
def base_policy(FS_list, gridsize, num_moves, flyPolicyType):
    current_FS = FS_list[len(FS_list)-1]

    spider_0_action = base_policy_spider(current_FS, gridsize, 0)
    spider_1_action = base_policy_spider(current_FS, gridsize, 1)
    if spider_0_action != None:
        new_FS = move(current_FS, spider_0_action, True, 0)   
        if spider_1_action != None:

            new_FS_2 = move(new_FS, spider_1_action, True, 1)

            # move the flies
            new_FS_3 = move_flies(new_FS_2, gridsize, flyPolicyType)
            FS_list.append(new_FS_3)
             
            #keep going as the spiders still have flies left to eat
            return base_policy(FS_list, gridsize, num_moves+2, flyPolicyType)
        else:
            #append new FS state from actions done by spiders with the moves from the flies
            new_FS_2 = move_flies(new_FS, gridsize, flyPolicyType)
            FS_list.append(new_FS_2)
            return (FS_list, num_moves+1)
    else:
        return (FS_list, num_moves)


#a function that returns the updated list of gamestates FS_list and number of moves thus far that have been done for the ordinary rollout policy, adding on one move for each spider to the list
def ordinary_rollout(FS_list, gridsize, num_moves, flyPolicyType):
    current_FS = FS_list[len(FS_list)-1]
    flies, spiders = current_FS


    if len(flies) == 0: return FS_list, num_moves

    best_new_fs = None
    best_num_moves = float("inf")
    #try all action combos, find heuristic to see #moves afterward, then choose minimum action
    for a0 in legal_actions(spiders[0], gridsize):
        for a1 in legal_actions(spiders[1], gridsize):
            #determine world state
            new_fs = move(current_FS, a0, True, 0)
            new_fs2 = move(new_fs, a1, True, 1)

            #create new FS list just to test base policy
            new_fs_list = FS_list.copy()
            new_fs_list.append(new_fs2)
            #find heuristic #moves 
            bp_fs_list, bp_num_moves = base_policy(new_fs_list, gridsize, num_moves+2, flyPolicyType)
            if bp_num_moves < best_num_moves:
                best_num_moves = bp_num_moves
                best_new_fs = new_fs2
    #move flies from best_new_fs
    best_new_fs_moved = move_flies(best_new_fs, gridsize, flyPolicyType)
    FS_list.append(best_new_fs_moved)
    return ordinary_rollout(FS_list, gridsize, num_moves+2, flyPolicyType)


#a function that returns the updated list of gamestates FS_list and number of moves thus far that have been done for the mulitagent rollout policy, adding on one move for each spider to the list
def multiagent_rollout(FS_list, gridsize, num_moves, flyPolicyType):
    current_FS = FS_list[len(FS_list)-1]
    flies, spiders = current_FS

    if len(flies) == 0: return (FS_list, num_moves)

    best_new_fs = None
    best_num_moves = float("inf")
    for a0 in legal_actions(spiders[0], gridsize):
        new_fs = move(current_FS, a0, True, 0)
        spider1_expected = base_policy_spider(new_fs, gridsize, 1)

        #create new FS_list to test base policy
        new_fs_list = FS_list.copy()

        if spider1_expected != None:
            new_fs2 = move(new_fs, spider1_expected, True, 1)
        
            new_fs_list.append(new_fs2)
            bp_fs_list, bp_num_moves = base_policy(new_fs_list, gridsize, num_moves+2, flyPolicyType)
        else:
            new_fs_list.append(new_fs)
            bp_fs_list, bp_num_moves = base_policy(new_fs_list, gridsize, num_moves+1, flyPolicyType)
        #find heuristic #moves
        if bp_num_moves < best_num_moves:
            best_num_moves = bp_num_moves
            best_new_fs = new_fs

    #if the flies are now 0 before spider 1 moves
    if len(best_new_fs[0]) == 0: 
        #move flies from best_new_fs
        best_new_fs_moved = move_flies(best_new_fs, gridsize, flyPolicyType)
        FS_list.append(best_new_fs_moved)
        return (FS_list, num_moves+1)
    best_new_fs2 = None
    best_num_moves = float("inf")
    for a1 in legal_actions(spiders[1], gridsize):
        #assume spider0 did best move in best_new_fs & move on from there
        new_fs2 = move(best_new_fs, a1, True, 1)
        
        #create new FS list to test base policy
        new_fs_list = FS_list.copy()
        new_fs_list.append(new_fs2)
        #find heuristic #moves
        bp_fs_list, bp_num_moves = base_policy(new_fs_list, gridsize, num_moves+2, flyPolicyType)
        if bp_num_moves < best_num_moves:
            best_num_moves = bp_num_moves
            best_new_fs2 = new_fs2

    #move flies from best_new_fs_2
    best_new_fs2_moved = move_flies(best_new_fs2, gridsize, flyPolicyType)
    FS_list.append(best_new_fs2_moved)
    return multiagent_rollout(FS_list, gridsize, num_moves+2, flyPolicyType)

#method to read in an initial state
#example commandline: python courtney_code.py --DP_type 2 --output_type 0 --init_type 1 --init_filename sample_init_state.txt
def get_initial_state_from_file(filename):
    flies_init = []
    spiders_init = []
    f = open(filename, "r")

    #split each fly by space and subsequent line spider by space
    flies = f.readline().split(' ')
    spiders = f.readline().split(' ')

    #split x and y coordinates by comma
    for fly in flies:
        (str_x, str_y) = fly.split(',')
        x = int(str_x)
        y = int(str_y)
        flies_init.append((x, y))

    for spider in spiders:
        (str_x, str_y) = spider.split(',')
        x = int(str_x)
        y = int(str_y)
        spiders_init.append((x, y))


    f.close()
    return (flies_init, spiders_init)


#parameters:
# - gridsize: an (x, y) tuple specifying the x and y dimensions of the grid
# - spiders: the number of spiders on the grid
# - flies: the number of flies on the grid
#
#return: 
# - tuple (flies_init, spiders_init):
#   - flies_init - a list of coordinates (x, y) for each fly i.e. [(1, 2), (3, 4)]
#   - spiders_init - same as flies, but spider coordinates

#example commandline (GIF multiagent rollout): python courtney_code.py --DP_type 2 --output_type 1 --init_type 0 --gridxy 15 --spiders 4 --flies 10
#
#Description: We take in the homies and apply a randomizer to each entity
def random_initial_state(gridsize, spiders, flies): 
    # We activate our randomizer roller
    flies_init = []
    spiders_init = []
    # Randomizer for spider locations
    for s in range(0,spiders):
        randx = random.randint(0,gridsize[0]-1)
        randy = random.randint(0,gridsize[1]-1)
        spiders_init.append((randx,randy))
    # Randomizer for fly locations
    for f in range(0,flies):
        randx = random.randint(0,gridsize[0]-1)
        randy = random.randint(0,gridsize[1]-1)
        flies_init.append((randx,randy))
    # return tuple
    return (flies_init, spiders_init)


#FLY MOVING/INTELLIGENCE

#funciton that determines & returns the move for a fly to go to the nearest wall
#if in a corner, the chosen move is to stay still (can change this later if we choose)
def base_policy_fly(gridsize, fly):
    #if in corner, stay still
    if (fly == (0, 0)) | (fly == (gridsize[0]-1, 0)) | (fly == (0, gridsize[1]-1)) | (fly == (gridsize[0]-1, gridsize[1]-1)):
        return Action.STILL

    #get legal actions

    best_action = None
    min_wall_distance = max(gridsize[0], gridsize[1])+1

    #out of legal actions, check to see if each wall is the best & find best action
    for action in legal_actions(fly, gridsize):
        if action == Action.LEFT:
            #distance to left wall is the x coord
            if fly[0] < min_wall_distance:
                min_wall_distance = fly[0]
                best_action = action
            elif (fly[0] == 0) & (fly[0] == min_wall_distance):
                min_wall_distance = fly[0]
                best_action = action
        elif action == Action.RIGHT:
            distance_to_right_wall = gridsize[0] - 1 - fly[0]
            if distance_to_right_wall < min_wall_distance:
                min_wall_distance = distance_to_right_wall
                best_action = action
            elif (distance_to_right_wall == 0) & (distance_to_right_wall == min_wall_distance):
                min_wall_distance = distance_to_right_wall
                best_action = action
        elif action == Action.UP:
            #distance to upper wall is the y coord
            if fly[1] < min_wall_distance:
                min_wall_distance = fly[1]
                best_action = action
            elif (fly[1] == 0) & (fly[1] == min_wall_distance):
                min_wall_distance = fly[1]
                best_action = action
        elif action == Action.DOWN:
            distance_to_bottom_wall = gridsize[1] - 1 - fly[1]
            if distance_to_bottom_wall < min_wall_distance:
                min_wall_distance = distance_to_bottom_wall
                best_action = action
            elif (distance_to_bottom_wall == 0) & (distance_to_bottom_wall == min_wall_distance):
                min_wall_distance = distance_to_bottom_wall
                best_action = action

    return best_action


#function to determine moves based on a specified policy & move the fliessssss BZZZZZZZZZZZZZZZZZZZz
# flyPolicyType: move flies (0) not at all (1) toward nearest wall - base policy 
# will likely add more flyPolicyTypes if we want fancier fly intelligence
def move_flies(FS, gridsize, flyPolicyType):
    #if the flies don't move or aren't there anymore, just return the game state FS as is
    if (flyPolicyType == 0) | (len(FS[0]) == 0):
        return FS

    #add all fly moves based on base policy to a new gamestate FS & return that
    new_FS = FS
    #if a fly runs into a spider, the indexes will change, so check for that
    original_fly_length = len(FS[0])
    flyIndex = 0
    while flyIndex < len(new_FS[0]):
        fly_move = base_policy_fly(gridsize, new_FS[0][flyIndex])
        new_FS = move(new_FS, fly_move, False, flyIndex)
        if len(new_FS[0]) < original_fly_length:
            difference = original_fly_length - len(new_FS[0])
            original_fly_length = len(new_FS[0])
            flyIndex -= difference

        flyIndex += 1

    
    return new_FS



#the main function where all of the commandline arguments are parsed, the game is initialized, and the specified policy is executed with the given output type
def main():
    parser = argparse.ArgumentParser(prog = 'Flies and Spiders',
                                      description = 'Runs a heuristic base policy, ordinary rollout with this heuristic, and multiagent rollout with the heuristic on the Flies and Spiders problem and prints to console, in GIF format, or creates a series of images')
    parser.add_argument('--DP_type', type=int, required=False, help='type of DP to run: (0) for base heuristic policy (1) for ordinary rollout with base heuristic and one lookahead (2) for multiagent rollout with base heuristic and one lookahead', default=0)
    parser.add_argument('--output_type', type=int, required=False, help='way to print output: (0) to print to console (1) to create a GIF or (2) to make a folder with a series of images', default=0)
    parser.add_argument('--GIF_name', type=str, required=False, help='for GIF output, can specify the name of the file output', default='animation')
    parser.add_argument('--image_folder', type=str, required=False, help='for image output, specify the path to a folder to be created & to store the images in', default='./output')
    parser.add_argument('--gridx', type=int, required=False, help='Specify how large the grid\'s x dimension should be', default=10)
    parser.add_argument('--gridy', type=int, required=False, help='Specify how large the grid\'s y dimension should be', default=10)
    parser.add_argument('--gridxy', type=int, required=False, help='For a square grid, specify how large the grid\'s x and y should be')
    parser.add_argument('--init_type', type=int, required=False, help='How the initial state will be specified: (0) randomly (1) specified (2) default', default=2)
    parser.add_argument('--init_filename', type=str, required=False, help='If an initial state is specified, read the initial state from this file')
    parser.add_argument('--spiders', type=int, required=False, help='For a random initial state, how many spiders should be on the board?', default=2)
    parser.add_argument('--flies', type=int, required=False, help='For a random initial state, how many flies should be on the board?', default=5)
    parser.add_argument('--fly_policy_type', type=int, required=False, help='How the flies should move (0) no movement (1) move towards the nearest wall/corner', default=0)

    args = parser.parse_args()

    #determine gridsize 
    if args.gridxy is not None:
        gridsize = (args.gridxy, args.gridxy)
    else:
        gridsize = (args.gridx, args.gridy)

    flyPolicyType = args.fly_policy_type

    #determine initial state
    random.seed()
    match args.init_type:
        case 0: (flies_init, spiders_init) = random_initial_state(gridsize, args.spiders, args.flies)
        case 1: (flies_init, spiders_init) = get_initial_state_from_file(args.init_filename)
        case 2: 
            #initial game board
            flies_init = [(8, 2), (2, 3), (4, 6), (1, 7), (8, 8)]
            spiders_init = [(6, 0), (6, 0)]
    print(flies_init)
    print(spiders_init)

    
    FS_list = [(flies_init, spiders_init)]
    num_moves = 0

    match args.DP_type:
        case 0: 
            FS_list, num_moves = base_policy(FS_list, gridsize, 0, flyPolicyType)
            print("--------------------Base Policy w/ Manhattan Heuristic--------------------")
        case 1: 
            FS_list, num_moves = ordinary_rollout(FS_list, gridsize, 0, flyPolicyType)
            print("-----------Ordinary Rollout w/ Manhattan Heuristic One Lookahead-----------")
        case 2: 
            FS_list, num_moves = multiagent_rollout(FS_list, gridsize, 0, flyPolicyType)
            print("----------Multiagent Rollout w/ Manhattan Heuristic One Lookahead----------")

    match args.output_type:
        case 0: print_output(FS_list)
        case 1: plot_animate(FS_list, gridsize, args.GIF_name)
        case 2: plot_images(FS_list, gridsize, args.image_folder)

    print("Number of moves needed:", num_moves)

if __name__ == "__main__":
    main()

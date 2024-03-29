import sys, argparse
import image_grid
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
import shutil
import random
import time
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
    if action == None:
        print("ERROR: Action type cannot be none.")
        exit(1)
    moving_list = [] #the list of spiders/flies for the spider/fly we're moving
    flies = FS[0].copy()
    spiders = FS[1].copy()
    if isASpider == True:
        moving_list = spiders #start with same spiders but change one
    else:
        moving_list = flies #start with same flies but change one

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
    else:
        print("ERROR: INVALID ACTION ", str(action))
        return None

    moving_list[index] = new_coords


    if isASpider == False:
        spiders = FS[1].copy()
        #if spider eats a fly, get rid of fly
        for spider in FS[1]:
            if new_coords == spider:
                flies.remove(new_coords)
                break #in case more than one spider is in the square

    else:
        #if spider eats a fly, get rid of fly
        for fly in FS[0]:
            if new_coords == fly:
                flies.remove(fly)
                break

    return (flies, spiders)

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
    spider_actions = []
    new_FS = current_FS
    
    #move each spider individually until either 1) all flies are eaten where we return the current FS_list or 2) all spiders have moved
    for spiderIndex in range(0, len(current_FS[1])):
        spider_action = base_policy_spider(current_FS, gridsize, spiderIndex)
        if spider_action != None:
            new_FS = move(new_FS, spider_action, True, spiderIndex)
            spider_actions.append(spider_action)
        else:
            #if we're not starting with no flies, then we have terminated by moving a spider to eat a fly,
            #so we need to note what spider(s) moved by updating the game state
            if new_FS != current_FS:
                FS_list.append(new_FS)

            #we have terminated before all spiders have moved, so add the number of spiders that have moved to the num_moves
            return (FS_list, num_moves+spiderIndex)

        
    #if we still have flies by the end of the spiders' turn, calculate the next moves for the flies and then spiders, etc.

    new_FS_2 = move_flies(new_FS, gridsize, flyPolicyType, num_moves)
    FS_list.append(new_FS_2)
    return base_policy(FS_list, gridsize, num_moves+len(current_FS[1]), flyPolicyType)
     
#function that acts as recursive nested for loops that determines the best FS based on the base policy
# and returns that new best FS to the ordinary_rollout function
def ordinary_rollout_best_FS(FS_list, gridsize, action_list, num_moves, spiderIndex, flyPolicyType):
    current_FS = FS_list[len(FS_list)-1]
    best_new_fs = None
    best_num_moves = float("inf")
    for action in legal_actions(current_FS[1][spiderIndex], gridsize):
        #add the action for this spider to the list
        new_action_list = action_list.copy()
        new_action_list.append(action)

        #if we're at the end then we are in the innermost for loop, now we need to move the spiders and compare values
        if spiderIndex ==len(current_FS[1])-1:
            new_FS = current_FS
            for i in range(0, len(new_action_list)):
                new_FS = move(new_FS, new_action_list[i], True, i)

            #at end we need to make the flies move
            new_FS = move_flies(new_FS, gridsize, flyPolicyType, num_moves)

            #create new FS list just to test base policy
            new_fs_list = FS_list.copy()
            new_fs_list.append(new_FS)
            #find heuristic #moves 
            bp_fs_list, bp_num_moves = base_policy(new_fs_list, gridsize, num_moves+len(current_FS[1]), flyPolicyType)
            if bp_num_moves < best_num_moves:
                best_num_moves = bp_num_moves
                best_new_fs = new_FS

        elif spiderIndex < len(current_FS[1])-1:
            new_action_list = action_list.copy()
            new_action_list.append(action)
            new_FS, new_num_moves = ordinary_rollout_best_FS(FS_list, gridsize, new_action_list, num_moves, spiderIndex+1, flyPolicyType)
            if new_num_moves < best_num_moves:
                best_num_moves = new_num_moves
                best_new_fs = new_FS
        else:
            print("ERROR: INDEX OUT OF BOUNDS FOR ORDINARY ROLLOUT")
    if best_new_fs == None:
        best_num_moves = float("inf")

    return best_new_fs, best_num_moves


#a function that returns the updated list of gamestates FS_list and number of moves thus far that have been done for the ordinary rollout policy, adding on one move for each spider to the list
def ordinary_rollout(FS_list, gridsize, num_moves, flyPolicyType):
    current_FS = FS_list[len(FS_list)-1]
    flies, spiders = current_FS

    #if there are no flies left, we're done, so terminate

    if len(flies) == 0: return FS_list, num_moves

    #determine best actions to take and the new FS gamestate for that
    best_new_fs, best_num_moves = ordinary_rollout_best_FS(FS_list, gridsize, [], num_moves, 0, flyPolicyType)
    #if the new FS for some reason is None, then it wasn't good enough so just return the number of moves as infinity
    if best_new_fs == None:
        return FS_list, float("inf")

    #append the new FS
    FS_list.append(best_new_fs)
    #continue rollout since we have more flies to catch
    return ordinary_rollout(FS_list, gridsize, num_moves+len(current_FS[1]), flyPolicyType)

#a function that returns the updated list of gamestates FS_list and number of moves thus far that have been done for the mulitagent rollout policy, adding on one move for each spider to the list
def multiagent_rollout(FS_list, gridsize, num_moves, flyPolicyType):
    current_FS = FS_list[len(FS_list)-1]
    flies, spiders = current_FS

    if len(flies) == 0: return (FS_list, num_moves)

    starting_fs = current_FS

    for spiderIndex in range(0, len(current_FS[1])):
        best_new_fs = None
        best_num_moves = float("inf")


        for action in legal_actions(spiders[spiderIndex], gridsize):
            new_fs = move(starting_fs, action, True, spiderIndex)
            new_fs_2 = new_fs
            #create new FS_list to test base policy
            new_fs_list = FS_list.copy()


            num_spiders_moved = 1+spiderIndex
            #make a list of the base policy for rest of spiders to see how that would play out
            for spiderIndex2 in range(spiderIndex+1, len(starting_fs[1])):
                next_spider_expected = base_policy_spider(new_fs_2, gridsize, spiderIndex2)

                if next_spider_expected != None:
                    new_fs_3 = move(new_fs_2, next_spider_expected, True, spiderIndex2)
                    if spiderIndex2 == len(starting_fs[1]) - 1:
                        new_fs_list.append(new_fs_3)
                    new_fs_2 = new_fs_3
                    num_spiders_moved += 1 #another spider has an action that isn't None, so it moved
                else:
                    new_fs_list.append(new_fs_2)
                    break

            if spiderIndex == len(starting_fs[1]) - 1:
                new_fs_list.append(new_fs)

            bp_fs_list, bp_num_moves = base_policy(new_fs_list, gridsize, num_moves+num_spiders_moved, flyPolicyType)
            #find heuristic #moves
            if bp_num_moves < best_num_moves:
                best_num_moves = bp_num_moves
                best_new_fs = new_fs
            
        #if the flies are now 0 before next spider moves
        if len(best_new_fs[0]) == 0: 
            #move flies from best_new_fs
            best_new_fs_moved = move_flies(best_new_fs, gridsize, flyPolicyType, num_moves)
            FS_list.append(best_new_fs_moved)
            return (FS_list, num_moves+spiderIndex +1)
        elif spiderIndex == len(current_FS[1]) -1:
            best_new_fs_moved = move_flies(best_new_fs, gridsize, flyPolicyType, num_moves)
            FS_list.append(best_new_fs_moved)
            return multiagent_rollout(FS_list, gridsize, num_moves+len(current_FS[1]), flyPolicyType)
        else:
            starting_fs = best_new_fs







#method to read in an initial state
#example commandline: python courtney_code.py --DP_type 2 --output_type 0 --init_type 1 --init_filename sample_init_state.txt --gridxy 16
def get_initial_state_from_file(filename):
    flies_init = []
    spiders_init = []
    f = open(filename, "r")


    #remove extra brackets/parentheses & split each fly by space and subsequent line spider by space
    flies_line = f.readline()
    flies_line = flies_line.replace('[(', '')
    flies_line = flies_line.replace(')]', '')
    flies_line = flies_line.replace('(', '')
    flies_line = flies_line.replace('\n', '')
    flies = flies_line.split('), ')
    spiders_line = f.readline()
    spiders_line = spiders_line.replace('[(', '')
    spiders_line = spiders_line.replace(')]', '')
    spiders_line = spiders_line.replace('(', '')
    spiders_line = spiders_line.replace('\n', '')
    spiders = spiders_line.split('), ')


    #split x and y coordinates by comma
    for fly in flies:
        (str_x, str_y) = fly.split(', ')
        x = int(str_x)
        y = int(str_y)
        flies_init.append((x, y))

    for spider in spiders:
        (str_x, str_y) = spider.split(', ')
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

#function that determines & returns the move for a fly to go to the nearest wall
#if in a corner, the chosen move is to stay still (can change this later if we choose)
def base_heuristic_fly(gridsize, fly):
    #if in corner, stay still
    if (fly == (0, 0)) or (fly == (gridsize[0]-1, 0)) or (fly == (0, gridsize[1]-1)) or (fly == (gridsize[0]-1, gridsize[1]-1)):
        return Action.STILL

    best_action = None
    min_wall_distance = max(gridsize[0], gridsize[1])+1
    legals = legal_actions(fly, gridsize)

    #out of legal actions, check to see if each wall is the best & find best action
    if Action.LEFT in legals:
        #distance to left wall is the x coord
        if (fly[0] < min_wall_distance) & (fly[0] > 0) & (fly[0] < gridsize[0] // 2 + 1):
            min_wall_distance = fly[0]
            best_action = Action.LEFT
    if Action.RIGHT in legals:
        distance_to_right_wall = gridsize[0] - 1 - fly[0]
        if (distance_to_right_wall < min_wall_distance) & (distance_to_right_wall > 0) & (distance_to_right_wall < gridsize[0] // 2 + 1):
            min_wall_distance = distance_to_right_wall
            best_action = Action.RIGHT
    if Action.UP in legals:
        #distance to upper wall is the y coord
        if (fly[1] < min_wall_distance) & (fly[1] > 0) & (fly[1] < gridsize[1] // 2 + 1):
            min_wall_distance = fly[1]
            best_action = Action.UP
    if Action.DOWN in legals:
        distance_to_bottom_wall = gridsize[1] - 1 - fly[1]
        if (distance_to_bottom_wall < min_wall_distance) & (distance_to_bottom_wall > 0) & (distance_to_bottom_wall < gridsize[1] // 2 + 1):
            min_wall_distance = distance_to_bottom_wall
            best_action = Action.DOWN

    #if som
    if best_action == None:
        print(fly)

    return best_action



#function that determines & returns the move for a fly to avoid closest spider if it's within 3 units (using manhattan distance)
def avoid_policy_fly(spiders, gridsize, fly):
    closest_spider = spiders[0]
    min_dist = manhattan_distance(fly, spiders[0])

    for spider in spiders[1:]:
        dist = manhattan_distance(spider, fly)
        if dist < min_dist:
            min_dist = dist
            closest_spider = spider
        #tiebreaker is vertical distance (for funsies let's make it different than the spider's tiebreaker)
        elif min_dist == dist:
            #determine which is more vertical
            if abs(spider[1]-fly[1]) < abs(closest_spider[1] - fly[1]):
                min_dist = dist
                closest_spider = spider
    #be lazy and only move if the spider is w/in 2 units
    if min_dist > 3:
        return Action.STILL
    best_action = None
    legals = legal_actions(fly, gridsize)
    if (fly[1] - closest_spider[1]) > 0 and Action.DOWN in legals:
        best_action = Action.DOWN
    elif (fly[1] - closest_spider[1]) < 0 and Action.UP in legals:
        best_action = Action.UP
    else:
        if (fly[0] - closest_spider[0]) > 0 and Action.RIGHT in legals:
            best_action = Action.RIGHT
        elif (fly[0] - closest_spider[0]) < 0 and Action.LEFT in legals:
            best_action = Action.LEFT
        else:
            #if we're here, then we're pushed up againsta nd edge and in lign with the spider, so use the corner strategy
            best_action = base_heuristic_fly(gridsize, fly)



    return best_action




#function to determine moves based on a specified policy & move the fliessssss BZZZZZZZZZZZZZZZZZZZz
# flyPolicyType: move flies (0) not at all (1) toward nearest wall - base policy (2) avoid closest spider w/in 3 units (3) rollout with avoid policy
# will likely add more flyPolicyTypes if we want fancier fly intelligence
def move_flies(FS, gridsize, flyPolicyType, num_moves):
    #if the flies don't move or aren't there anymore, just return the game state FS as is
    if (flyPolicyType == 0) | (len(FS[0]) == 0):
        return FS

    #add all fly moves based on base policy to a new gamestate FS & return that
    new_FS = FS
    #if a fly runs into a spider, the indexes will change, so check for that
    original_fly_length = len(FS[0])
    flyIndex = 0
    while flyIndex < len(new_FS[0]):
        if flyPolicyType == 1:
            fly_move = base_heuristic_fly(gridsize, new_FS[0][flyIndex])
            print(fly_move)
        elif flyPolicyType == 2:
            fly_move = avoid_policy_fly(new_FS[1], gridsize, new_FS[0][flyIndex])
        else:
            #if we are tasked with rollout with more than 1 fly, that is not implemented
            #so just run the base policy instead
            fly_move = base_heuristic_fly(gridsize, new_FS[0][flyIndex])
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
    parser.add_argument('--fly_policy_type', type=int, required=False, help='How the flies should move (0) no movement (1) move towards the nearest wall/corner (2) move away from the closest spider w/in 3 units or else stay still (3) perform rollout based on spider moves', default=0)

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
    start_time = time.time() 
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

    end_time = time.time()
    total_time = end_time - start_time
    print(f'Time taken: {total_time:.4f}s')
    match args.output_type:
        case 0: print_output(FS_list)
        case 1: plot_animate(FS_list, gridsize, args.GIF_name)
        case 2: plot_images(FS_list, gridsize, args.image_folder)

    print("Number of moves needed: ", num_moves)

if __name__ == "__main__":
    main()

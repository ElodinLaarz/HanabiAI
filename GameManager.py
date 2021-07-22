from HanabiGame import HanabiGame
from HanabiPlayer import HanabiPlayer

import numpy as np
import random
# import statistics


# Genetic Algorithm Stuff

def create_offspring_weights(parents):
    all_weights = [list(parent.get_weights()) for parent in parents]
    average_weights = []
    for i in range(len(all_weights[0])):
        average_weights.append(sum([weight[i]/len(all_weights) for weight 
                                    in all_weights]))
        
    return mutate(average_weights)

def mutate(weights, mutation_rate=0.01):
    new_weights = []

    for weight in weights:
        if random.random() < mutation_rate:
            new_weights.append(random.random())
        else:
            new_weights.append(weight)

    return np.array(new_weights)

# Turn a collection of various dimensional arrays into a single, long array

def flatten(list_to_flatten):
        found_something_to_flatten = True
        while(found_something_to_flatten == True):
            found_something_to_flatten = False
            temp_list = []
            for i, item in enumerate(list_to_flatten):
                if isinstance(item, list):
                    found_something_to_flatten = True
                    temp_list += list_to_flatten[i]
                else:
                    temp_list.append(list_to_flatten[i])
            list_to_flatten = temp_list
        return list_to_flatten
    
test_game = HanabiGame()

flat_state = flatten(test_game.boardState(0))
input_size = len(flat_state) # This equals 144 in 2 player normal game
print(f"The input length is {input_size}.")

# Genetic Algorithm to find a good HanabiAI
# Initialize with 2*N players (Initial Population)

population = 50
# The weights in this current implementation are 5,440
num_weights = 5440

# current_generation_players = prev_gen
current_generation_players = []

for i in range(population):
    # [Player, score_achieved]
    random_weights = np.random.rand(num_weights)
    current_generation_players.append([HanabiPlayer(game_state_size=input_size,
                                                weights=random_weights), 0])

    
# Evalute the fitness of each player (which we'll consider to be the 
# maximum score obtained before game ends.)

# I am going to implement it now where pairs of players play different games, 
# but maybe it'd be better to have all pairs of players play through the same 
# game for fairness. If they happen to play an easy game
# They might get a bias.

#How many times will we train the group?
num_gen_to_train = 10000

for i in range(num_gen_to_train):
    # Sort randomly and take pairs in order as game partners
    # random.shuffle(current_generation_players)
        
    for j in range(population):
        cur_game = HanabiGame()
#         player_turn = 0
        while cur_game.game_end == False:
            # Predict a move
            np_bs = np.array(flatten(cur_game.boardState(
                                            cur_game.current_player_turn)))
            move_ratings = (current_generation_players
                                    [j][0].choose_best_move(np_bs))
            move_index = 0
            
            
            # If we are out of hints, play/discard
            # This is a hack atm, where on the final round of the game, 
            # the players will only play/discard and not give hints, 
            # which is not necessarily optimal.
            if cur_game.hints <= 0 or cur_game.game_is_ending:
                move_index = move_ratings[:10].argmax()
            else:
                move_index = move_ratings.argmax()
            # print(f"We are attempting to perform move {move_index} with 
            # {cur_game.hints} hints.")
            # print(move_index)
            cur_game.performMove(move_index)
        # Score the players this time
        current_generation_players[j][1]=cur_game.current_score

#     We have  changed the fitness to throw out those who score zero... gl us!
    fitness_from_score = [(x[1])**4 for x in current_generation_players]
    normalized_fitness = np.array(fitness_from_score) / np.sum(
                                                        fitness_from_score)
    
    print(f"Fitness = {normalized_fitness}")

    
    # Save weights after training? Or maybe save N of them?
    # print(current_generation_players[0])
    sorted_gen = sorted(current_generation_players, key=lambda x: x[1], 
                        reverse=True)
    zeros = 0
    while (sorted_gen[-(zeros+1)][1] == 0):
        zeros += 1
    print(f"In generation {i} there were {zeros} " +
          "players who scored 0 points.\n")
    print(f"First place in generation {i} scored : {sorted_gen[0][1]}")
    print(f"Last place in generation {i} scored : {sorted_gen[-1][1]}")
    f = open("./weights/genetic_weights.txt", "a")
    f.write(f"Best of gen {i} scored {sorted_gen[0][1]} : \n" + 
            str(sorted_gen[0][0].get_weights()) + "\n")
    f.close()

    
    # Generate a new generation by randomly choosing two* parents biased upon 
    # fitness.
    # Create a child with new weights based upon the cross-over of parents
    
    new_generation = []
    for j in range(population):
        # Two random parents chosen with score bias
        index_choice = list(range(len(current_generation_players)))
        parents = [np.random.choice(index_choice, p=normalized_fitness),
                   np.random.choice(index_choice, p=normalized_fitness)]
        parents = [current_generation_players[choice][0] for choice in parents]
#         print(parents)
        child_weights = create_offspring_weights(parents)
#         print(flatten(child_weights))
        new_generation.append(
            [HanabiPlayer(game_state_size=input_size,weights=child_weights),0])
    
    current_generation_players=new_generation




# Save the previous generation to run it through again.
# prev_gen = current_generation_players
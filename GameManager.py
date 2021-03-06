"""
GameManager creates a population of AI players, pairs them up, and runs
their games of Hanabi against one another. It then sorts the generation
of players chooses the most fit, and then creates a new generation with
weights that are biased towards the best of the previous generation.
[This idea is referred to as a 'Genetic Algorithm.']
"""

import glob
import os
import random

import numpy as np

from HanabiGame import HanabiGame
from HanabiPlayer import HanabiPlayer

def create_offspring_weights(cur_parents):
    """

    Parameters
    ----------
    cur_parents : list(HanabiPlayer)
        A list of HanabiPlayers whose weights will be used
        to create an offspring

    Returns
    -------
    list(float)
        a mutated list of the average of each of
        the parents' weights.

    """
    all_weights = [list(parent.get_weights()) for parent in cur_parents]
    average_weights = []
    for weight_index in range(len(all_weights[0])):
        average_weights.append(sum([weight[weight_index]/len(all_weights)
                                    for weight in all_weights]))

    return mutate(average_weights)

def mutate(weights, mutation_rate=0.002):
    """

    Parameters
    ----------
    weights : list(float)
        a list to be altered with some probability based upon mutation_rate
    mutation_rate : float, optional
        determines the frequency with which we replace a given value in
        weights. With the default value, you expect to replace about 1 in
        500 of the weights in the list. The default is 0.002.

    Returns
    -------
    list(float)
        the updated list of weights where a random number of items, based
        upon the value mutation_rate, in the list have been replaced by
        a random.uniform number between (-1,1).

    """
    new_weights = []

    for weight in weights:
        if random.random() < mutation_rate:
            new_weights.append(random.uniform(-1,1))
        else:
            new_weights.append(weight)

    return np.array(new_weights)


def flatten(list_to_flatten):
    """

    Parameters
    ----------
    list_to_flatten : list
        an arbitrary list of lists that we wish to be turned into a single
        list of the inner-most type.

    Returns
    -------
    list_to_flatten : list
        a list containing all items in the inner-most portion of the list
        given.

    """
    found_something_to_flatten = True
    while found_something_to_flatten :
        found_something_to_flatten = False
        temp_list = []
        for index, item in enumerate(list_to_flatten):
            if isinstance(item, list):
                found_something_to_flatten = True
                temp_list += list_to_flatten[index]
            else:
                temp_list.append(list_to_flatten[index])
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

# Import a couple high scores from previous attempts to seed
seed_weights = 0

weights_path = './weights/'
for filename in glob.glob(os.path.join(weights_path, '*.txt')):
    with open(os.path.join(os.getcwd(), filename), 'r') as f:
        print(f"Importing player who scored {f.readline()}")
        current_generation_players.append([HanabiPlayer(game_state_size =
                                                        input_size,
                    weights =np.array(f.readline().strip().split(', '))), 0])
        seed_weights += 1

for i in range(seed_weights, population):
    # [Player, score_achieved]
    random_weights = 2*np.random.rand(num_weights)-1
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
        while not cur_game.game_end :
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

    print(f"\nFitness = {normalized_fitness}\n")


    # Save weights after training? Or maybe save N of them?
    # print(current_generation_players[0])
    sorted_gen = sorted(current_generation_players, key=lambda x: x[1],
                        reverse=True)
    zeros = 0
    while sorted_gen[-(zeros+1)][1] == 0:
        zeros += 1
    print(f"In generation {i} there were {zeros} " +
          "players who scored 0 points.\n")
    print(f"First place in generation {i} scored : {sorted_gen[0][1]}")
    print(f"Last place in generation {i} scored : {sorted_gen[-1][1]}")

    # If a player gets a particular score, we save their scores to disk
    min_score_to_save = 9

    if sorted_gen[0][1] >= min_score_to_save:
        f = open(f"./weights/score{sorted_gen[0][1]}-gen{i}.txt", "w")
        f.write(f"{sorted_gen[0][1]} \n" +
                str(", ".join(list(map(str,sorted_gen[0][0].get_weights(
                                                                ))))) + "\n")
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

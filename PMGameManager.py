from HanabiGame import HanabiGame
from PMHanabiPlayer import ProbableMatrixHanabiPlayer as player

import glob
import numpy as np
import os
import statistics

# Input = [hints, lives, card_playable_probs, usefulness_of_hints]


test_game = HanabiGame()

# Lives, Hints, len(deck) 5 cards in hand, 3*opponents cards.
input_size = 2+5+2*10
# play cards (5), discard cards (5), give hints (10 x num_players)
output_size = 30

population = 1000

current_generation = []

# Import a couple high scores from previous attempts to seed
seed_weights = 0

weights_path = './three_player_weights/'
for filename in glob.glob(os.path.join(weights_path, '*.txt')):
    with open(os.path.join(os.getcwd(), filename), 'r') as f:
        f.readline()
        # print(f"Importing player who scored {f.readline()}");
        current_generation.append([player(input_size=input_size, 
                    output_size=output_size,
                    weights = np.array(f.readline().strip().split(', '), 
                                        dtype=float)), 0])
        seed_weights += 1

print(f"Finished importing {seed_weights} weights. \n\n")

# [Player, score]
for i in range(seed_weights, population):
    current_generation.append([player(input_size=input_size,
                                      output_size=output_size), 0])

num_generations = 1000

# If a player gets a particular score, we save their scores to disk
min_score_to_save = 11

for generation_index in range(num_generations):
    
    for player_index in range(population):
        
        # Makes sure a score wasn't a fluke! Have a player play more than one
        # game!
        games_to_play = 1
        player_scores = []
        for num_games in range(games_to_play):
            cur_game = HanabiGame(num_players=3)
            
            while cur_game.game_end == False:
                
                move_ratings = (current_generation[player_index][0]
                                .move_preference(cur_game.probabilities()))
                
                move_index = 0
                
                if cur_game.hints <= 0 or cur_game.game_is_ending:
                    move_index = move_ratings[:10].argmax()
                else:
                    move_index = move_ratings.argmax()
                    
                cur_game.performMove(move_index)
            # if cur_game.lives != 0:
            player_scores.append(cur_game.current_score)
            # else:
            #     player_scores.append(0)
        
        # print(player_scores)
        current_generation[player_index][1] = statistics.mean(player_scores)
    
    fitness_from_score = [(x[1])**4 for x in current_generation]
    normalized_fitness = np.array(fitness_from_score) / np.sum(
                                                        fitness_from_score)
    
    # print(f"\nFitness = {normalized_fitness}\n")
    
    # Save weights after training? Or maybe save N of them?
    # print(current_generation_players[0])
    sorted_gen = sorted(current_generation, key=lambda x: x[1], 
                        reverse=True)
    minimums = 0
    while (sorted_gen[-(minimums+1)][1] == sorted_gen[-1][1]):
        minimums += 1
    print(f"\n\nIn generation {generation_index} there were {minimums} " +
          f"players who scored {sorted_gen[-1][1]} points out of {population}"
          + " players.\n")
    print(f"First place in generation {generation_index} scored an average" +
          f" of : {sorted_gen[0][1]}")
    print(f"Last place in generation {generation_index} scored :" + 
          f" {sorted_gen[-1][1]}")
    
    weight_index_to_add = 0
    while sorted_gen[weight_index_to_add][1] >= min_score_to_save:
        f = open("./three_player_weights/"
                 +f"score{sorted_gen[weight_index_to_add][1]}-" + 
                 f"gen{generation_index}-{weight_index_to_add}.txt", "w")
        f.write(f"{sorted_gen[weight_index_to_add][1]} \n" + 
                str(", ".join(list(map(str,sorted_gen[0][0].get_weights(
                                                                ))))) + "\n")
        f.close()
        weight_index_to_add += 1
    
    # If we're consistently getting scores of a fixed value, increase the
    # target score
    if weight_index_to_add >= 3:
        min_score_to_save += 1
    
    # Generate a new generation by randomly choosing two* parents biased upon 
    # fitness.
    # Create a child with new weights based upon the cross-over of parents
    
    new_generation = []
    for j in range(population):
        # Two random parents chosen with score bias
        index_choice = list(range(len(current_generation)))
        parents = [np.random.choice(index_choice, p=normalized_fitness),
                   np.random.choice(index_choice, p=normalized_fitness)]
        parents = [current_generation[choice][0] for choice in parents]
        
        # print(parents[0].weights[0],parents[1].weights[0])
        child_weights = parents[0].make_child([parents[1]], 
                                              mutation_rate = 0.002)
        
        new_generation.append(
            [player(input_size=input_size,output_size=output_size,
                    weights=child_weights),0])
    
    current_generation = new_generation
            

test_player = player(input_size=input_size, output_size=output_size)
import numpy as np
import random
# import statistics
# import tensorflow as tf
# from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

from tensorflow.keras.optimizers import Adam
# from tensorflow.keras.metrics import categorical_crossentropy

class HanabiPlayer:
    
    # Game state will be ordered as
    # [[score]: 1, [lives remaining]: 1, [hints available]: 1,
    # [# cards in deck]: 1,[Cards in play]: num_suits, 
    # [Discards]: num_suits*num_values, [Hints in Hand], 
    # [Other People's Hands Hints]]
    def __init__(self, game_state_size, weights, num_players = 2):
        
        self.game_state_size = game_state_size
        self.num_players = 2
        
        # These are random. Just a guess!
        second_layer_size = 32
        third_layer_size = 16
        
        # Allows for modular layer sizes
        # The final layer is the number of possible moves to output.
        # There are always hand_size*2 (plays or discards) + num_opponents * 
        # (num_values + num_suits) (hints)
        # possible moves. FOR NOW -- We're gonna assume normal hand size with 
        # 5 suits and 5 values for convenience.
        # Hence, 5*2 + (num_players - 1)*10
        # I also put the game_state_size as the [-1] element since it 
        # 'comes before' 0. This is terrible. Why have I chosen to do this?
        self.layer_sizes = [second_layer_size, third_layer_size, 10+10*(
            self.num_players-1), game_state_size]
        
        self.model = Sequential([
            # Input will be a vector of game_state_size length
            Dense(units=self.layer_sizes[0], input_shape=(game_state_size,), 
                  use_bias=False, activation='relu'),
            Dense(units=self.layer_sizes[1], use_bias=False, 
                  activation='relu'),
            Dense(units=self.layer_sizes[2], use_bias=False, 
                  activation='sigmoid')
        ])
        
#         if any(weights == None):
#             self.weights = np.array([0]*((game_state_size)*64+64*16+16*20))
#         else:
        
        self.set_weights(weights)
        
        # Since we will be updating the weights ourselves, this isn't 
        # necessary...
        self.model.compile(optimizer=Adam(learning_rate=0.0001), 
             loss='sparse_categorical_crossentropy',metrics=['accuracy'])
    
    
    def get_weights(self):
        weights = []
        for i, layer in enumerate(self.model.layers):
            weights.extend(np.resize(layer.get_weights()[0], 
                        self.layer_sizes[i-1]*self.layer_sizes[i]).tolist())
#         print(weights)
        return weights
        
    # Set the given weights for the model
    def set_weights(self, np_flat_weights):
        if len(np_flat_weights) == (self.game_state_size*self.layer_sizes[0]+
                                    self.layer_sizes[0]*self.layer_sizes[1]+
                                    self.layer_sizes[1]*self.layer_sizes[2]):
            weights0 = (np_flat_weights
                        [:self.game_state_size*self.layer_sizes[0]].copy())
            weights1 = (np_flat_weights
                        [self.game_state_size*self.layer_sizes[0]: 
                         self.game_state_size*self.layer_sizes[0]+
                         self.layer_sizes[0]*self.layer_sizes[1]].copy())
            weights2 = (np_flat_weights
                        [-self.layer_sizes[1]*self.layer_sizes[2]:].copy())
            
#             print("final weight to be added: ", weights2[-1])
            
            weights0.resize(self.game_state_size,self.layer_sizes[0])
            weights1.resize(self.layer_sizes[0],self.layer_sizes[1])
            weights2.resize(self.layer_sizes[1],self.layer_sizes[2])

            self.model.layers[0].set_weights([weights0])
            self.model.layers[1].set_weights([weights1])
            self.model.layers[2].set_weights([weights2])
        else:
            print("Incorrect weight sizes.")
            
            return
        
    
    def choose_best_move(self, game_state):
        guess_vec = self.model.predict(np.array( [game_state,] ))
        
#         print(f"guess vec = {guess_vec}")
        return guess_vec[0]
                
    def update_game(self, game_state):
        self.game_state = game_state
        return
    
    def mutate(self, dna_weights):
        mutation_rate = 0.001
        new_weights = []
        
        for weight in dna_weights:
            if random.random() < mutation_rate:
                new_weights.append(random.random())
            else:
                new_weights.append(weight)
        
        return new_weights

# test_game = HanabiGame()
# input_size = len(flatten(test_game.boardState(0)))+len(test_game.legal_move_list[0])
# print(input_size)
# test_player = HanabiPlayer(game_state_size = input_size)
# # len(board_state) = 4 + num_suits + num_suits*num_values + hand_size*(num_suits+num_values+1)*num_players + len(move)
# # In 2 player, 5 cards, 5 suits, 5 values, you should get 144
# weights = test_player.model.get_weights()
# test_player.model.summary()
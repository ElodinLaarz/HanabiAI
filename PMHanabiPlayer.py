import numpy as np
import random

class ProbableMatrixHanabiPlayer:
    
    # This Hanabi player simply takes in all the probabilities from the board
    # and outputs a move by multiplying by a matrix of weights -- a sort
    # of no-hidden-layer-NN... Which is just a matrix.
    
    def __init__(self, input_size, output_size, weights = None):
        
        self.input_size = input_size
        self.output_size = output_size
        
        # If we did not receive specific weights, we will just create a
        # matrix of dimensions input_size x output_size filled with random
        # values between +/- 1.
        
        if weights is None:
            self.weights = 2*np.random.rand(output_size,input_size)-1
        elif input_size*output_size != len(weights):
            print('Weights are the wrong size.')
            print(f'Expected {output_size*input_size} and got {len(weights)}.')
            return
        else:
            self.set_weights(weights)

    
    # A move is determined by the matrix weights applied to the vector board,
    # which will be a list of the current probabilities in the order of
    # [Probabilties cards are playable, Probability cards are safe discards,
    # Which cards in opponents hands are playable/if they know or don't know.]

    def move_preference(self, board):
        # print(board)
        # print(self.weights[0])
        return (self.weights.dot(np.array(board)))
    
    def get_weights(self):
        return list(np.resize(self.weights, 
                              self.weights.shape[0] * self.weights.shape[1]))
    
    def set_weights(self, weights):
        self.weights = np.resize(np.array(weights),
                                    (self.output_size,self.input_size))
    
        
    # Given a list of partners, this returns a list of their average weights
    # with a chance to replace a weight with a random value between +/- 1.
    
    def make_child(self, partners, mutation_rate = 0.005):
        partners.append(self)
        all_weights = [partner.get_weights() for partner in partners]
        average_weights = []
        for i in range(len(all_weights[0])):
            average_weights.append(sum([weight[i]/len(all_weights) for weight 
                                        in all_weights]))
            
        return self.mutate(average_weights, mutation_rate)

    def mutate(self, weights, mutation_rate):
        new_weights = []
    
        for weight in weights:
            if random.random() < mutation_rate:
                new_weights.append(random.uniform(-1,1))
            else:
                new_weights.append(weight)
    
        return np.array(new_weights)
import itertools
import random

class HanabiGame:
    
    def __init__(self, hand_size = 5, hints = 8, lives = 3, num_players = 2, 
                 num_suits = 5, num_values = 5):
                    
        # Hand Size
        if hand_size < 1:
            print("How are you going to play " +
                  "without any cards in your hand, silly?")
        self.hand_size = hand_size
        
        # Hints remaining
        self.hints = hints
        self.max_hints = self.hints
        
        # Lives remaining
        self.lives = lives

        # Number of players
        if num_players < 2:
            print("Hanabi must be played with at least two players.")
            
        self.num_players = num_players
        
        # Suits of Cards
        self.num_suits = num_suits
        self.suits = list(range(self.num_suits))

        # Values of Cards
        # There are 3 zeros of each suit, one of the maximal value, 
        # and two of all others.
        if num_values < 2:
            print("Please allow for at least two values.")
        
        self.num_values = num_values
        self.values = ([0, 0, 0] + list(range(1, self.num_values-1))*2 +
                       [self.num_values-1])

        # Deck
        # A card in the deck's ten's place is the suit of the card and 
        # the one's place is the value
        self.deck = [(suit,value) for suit, value in itertools.product(
                                                    self.suits,self.values)]

        # Cards in the Hands of each Player
        self.player_hands = [[] for i in range(num_players)]
        self.initialDeal()

        # Hint information available to each player
        # self.player_hints[0] = [Hints received for suits, Hints received 
        # for values, turns_in_hand]
        # Hints received are either 0 (no info), 1 (positive info), 
        # or -1 (negative info)
        # So, [[-1, 0, 0, 0, 0], [-1, 1, -1, -1, -1], 3] 
        # would correspond to knowing a card is NOT of suit 0 and IS of 
        # value 1 and has been in your hand for 3 turns.
        self.player_hints = ([[[[0]*self.num_suits,[0]*self.num_values, 0] 
                               for j in range(self.hand_size)]
                              for i in range(self.num_players)])
        
        # Keep track of whose turn it is
        self.current_player_turn = 0
        
        # Keep track of the score.
        # Note*: Normally in Hanabi your score is zero until the last turn
        # is played, but to help the AI, the current score will only become
        # zero when all lives are lost.
        self.current_score = 0
        
        # Cards that have been played onto the board
        # -1 corresponds to no card of a particular suit having been played.
        # The current value of self.board[i] = Highest value of card played
        # of that suit.
        self.board = [-1]*self.num_suits
        
        # Discard Pile
        # self.discards[i][j] = The number of suit i value j cards that 
        # have been discarded so far.
        self.discards = [[0]*num_values for i in range(self.num_suits)]
        
        # Keep a list of possible next moves
        self.legal_move_list = []
        # Initialize legal_move_list
        self.legalMoves()
        
        # Keep track of the number of moves left when the final round starts
        self.final_round_moves = self.num_players
        self.game_is_ending = False
        
        # When the game ends, the game manager should deal with cleaning 
        # everything up.
        self.game_end = False


    def initialDeal(self):
        random.shuffle(self.deck)
        for i in range(self.hand_size):
            for hand in range(self.num_players):
                self.player_hands[hand].append(self.deck.pop())
    
    # Returns the board state from a given player's perspective.
    # In particular, it returns all public information and the cards in 
    # the opponents hands.
    # [[score]: 1, [lives remaining]: 1, [hints available]: 1, 
    # [# cards in deck]: 1, [Cards in play]: num_suits, 
    # [Discards]: num_suits*num_values, [Hints in Hand], 
    # [Other People's Hands Hints]]
    def boardState(self, player_number):
        return ([self.current_score, self.lives, self.hints, len(self.deck), 
                self.board, self.discards, self.player_hints[player_number]] +
    [hint for i,hint in enumerate(self.player_hints) if i!= player_number])
    
    def printBoardState(self, player_number=-1):
        
        # If no player is specified, return the view from the current player
        if player_number == -1:
            player_number = self.current_player_turn
#         cur_board = boardState(player_number)
        print(f"From the perspective of player {player_number}")
        print(f"The current score is {self.current_score}.")
        print(f"You have {self.lives} lives and {self.hints} hints left.")
        print(f"There are {len(self.deck)} cards left in the deck.")
        for i, max_card in enumerate(self.board):
            if max_card == -1:
                print(f"You have not played any cards of suit {i}")
            elif max_card == 0:
                print(f"You have played the 0 of suit {i}.")
            else:
                print(f"You have played {max_card} cards of suit {i}.")
        
        for card_index, hint in enumerate(self.player_hints[player_number]):
            if hint == [[0]*self.num_suits, [0]*self.num_values, 0]:
                print(f"You don't know anything about card {card_index}.")
            else:
                if hint[0] == [0]*self.num_suits:
                    print("You don't know anything about the suit of " + 
                          f"card {card_index}.")
                else:
                    if 1 in hint[0]:
                        print(f"You know that {card_index} is of "+ 
                              f"suit {(hint[0]).index(1)}")
                    else:
                        for suit_index, existence in enumerate(hint[0]):
                            if existence == -1:
                                print(f"You know card {card_index} is "+ 
                                      f"not of suit {suit_index}.")
                
                if hint[1] == [0]*self.num_values:
                    print("You don't know anything about the value" + 
                          f"of card {card_index}.")
                else:
                    if 1 in hint[1]:
                        print(f"You know that {card_index} is of " + 
                              f"suit {(hint[0]).index(1)}")
                    else:
                        for value_index, existence in enumerate(hint[1]):
                            if existence == -1:
                                print(f"You know card {card_index} is not " +
                                      f"of value {value_index}.")

                            
    # Returns a tuple (The index of the current player's turn, 
    # [List of allowable moves])    
    def legalMoves(self):
        
        # Moves will be described by a tuple 
        # (Choose to Play/Discard/Hint, Index of Card to Discard/Play 
        # [-1 if giving hint instead], 
        # Hint Type[(player, suit, value)])
        # Hint Type is (-1,-1,-1) if not giving a hint.
        allowed_moves = []
        
        # Play moves (0,X,-1,-1)
        for i in range(self.hand_size):
            allowed_moves.append((0,i,-1,-1,-1))
        
        # Discard moves (1,X,-1,-1)
        for i in range(self.hand_size):
            allowed_moves.append((1,i,-1,-1,-1))
        
        
        # If hint available, hint moves (2, -1, Player, Suit, Value)
        if self.hints > 0:
            for player_index in range(self.num_players):
                if player_index != self.current_player_turn:
                    for suit_index in range(self.num_suits):
                        allowed_moves.append((2,-1,player_index,
                                              suit_index,-1))
                    for value_index in range(self.num_values):
                        allowed_moves.append((2,-1,player_index,
                                              -1,value_index))
        
        self.legal_move_list = allowed_moves
        return (self.current_player_turn, allowed_moves)
    
    def printLegalMoves(self):
        self.legalMoves()
        print(f"It is Player {self.current_player_turn}'s turn.")
        if len(self.legal_move_list) == 0:
            print("You done goofed. No legal moves.")
            return
        for index, move in enumerate(self.legal_move_list):
            if move[0] == 0:
                print(f"{index}: You can play your {move[1]} card.")
            elif move[0] == 1:
                print(f"{index}: You can discard your {move[1]} card.")
            else:
                if move[3] != -1:
                    print(f"{index}: You can tell player {move[2]} about " +
                          f"their cards of suit {move[3]}.")
                elif move[4] != -1:
                    print(f"{index}: You can tell player {move[2]} about " +
                          f"their cards of value {move[4]}.")
                else:
                    print('We definitely should not have gotten here.')
    
    # Current Player Draws a card
    def drawCard(self):
        if len(self.deck) == 0:
            self.game_is_ending = True
            self.final_round_moves -= 1
            if self.final_round_moves == 0:
                self.endGame()
            if len(self.player_hints[self.current_player_turn]) < 5:
                self.player_hints[self.current_player_turn].append(
                    [[0]*self.num_suits,[0]*self.num_values, 0])
            return

        if len(self.player_hands[self.current_player_turn]) != 4:
            print("A player is trying to draw with " + 
                  f"{len(self.player_hands[self.current_player_turn])} " + 
                  "cards in their hand.")
            return
        else:
            self.player_hands[self.current_player_turn].append(
                                                    self.deck.pop())
            self.player_hints[self.current_player_turn].append(
                                [[0]*self.num_suits,[0]*self.num_values, 0])
        
        self.legalMoves()
    
    # Implement this
    def endGame(self):
        self.game_end = True
        return
    
    def playCard(self, index):
        if index > len(self.player_hands[self.current_player_turn]):
            print("That card is unplayable. Uh oh.")
            return
        
        card = self.player_hands[self.current_player_turn][index]
        suit = card[0]
        value = card[1]
        
        
        # If the card is playable, play it, increment score, 
        # and draw a card.
        # Otherwise, we'll lose a life, check game end, discard it, 
        # and draw a card.
        if self.board[suit] + 1 == value:
            self.board[suit] = value
            self.current_score += 1
        else:
            self.lives -= 1
            if self.lives <= 0:
                self.endGame()
                return
        self.discardCard(index, gain_hint = False)
        self.drawCard()

    # Only draw a card if gain_hint = True
    # Update discard pile
    def discardCard(self, index, gain_hint = True):
        self.discards[self.player_hands[self.current_player_turn][index][0]][
                self.player_hands[self.current_player_turn][index][1]]+= 1
        del self.player_hands[self.current_player_turn][index]
        del self.player_hints[self.current_player_turn][index]
        if gain_hint == True:
            self.drawCard()
            if self.hints < self.max_hints:
                self.hints += 1
        return

    # If a hint is given whilst game is ending, remember to decrement 
    # final_round_moves
    # self.player_hints = [[[[0]*self.num_suits,[0]*self.num_values] 
    # for j in range(self.hand_size)]
    #                        for i in range(self.num_players)]
    def giveHint(self, hint):
        player, suit_hint, value_hint = hint[0], hint[1], hint[2]
        
        if self.hints <= 0:
            print("You cannot give a hint, as you have no hint tokens left!")
        
        # card_hints is of the form [[suit hints], [value hints]]
        for card_index, card_hints in enumerate(self.player_hints[player]):
            card_suit = self.player_hands[player][card_index][0]
            card_value = self.player_hands[player][card_index][1]
            if (suit_hint != -1):
                if suit_hint == card_suit:
                    card_hints[0] = [1 if x == card_suit else -1 
                                     for x in range(self.num_suits) ]
                else:
                    card_hints[0][suit_hint] = -1
            elif (value_hint != -1):
                if value_hint == card_value:
                    card_hints[1] = [1 if x == card_value else -1 
                                     for x in range(self.num_values) ]
                else:
                    card_hints[1][suit_hint] = -1
            else:
                print("We were given neither a suit nor a value.")
                return
        self.hints -= 1
        return

    
    def performMove(self, index = -1, move = None):
        self.legalMoves()
        if index == -1 and move == None:
            print("What move would you like to do?")
            return
        if index > len(self.legal_move_list):
            print("Choose a valid move. [Index out of range.]")
            return
        if move != None and move not in self.legal_move_list:
            print("Choose a valid move. [Move not legal.]")
            return

        if index != -1:
            move = self.legal_move_list[index]
        
#         print(move)
#         else:
#             index = legal_move_list.index(move)
        
        # Reminder: move = (play/discard/hint, card to play/discard index, 
        # player to give hint, suit hint, value hint)
        # Reminder: move[0]: 0 - Play, 1 - Discard, 2 - Hint
        if move[0] == 0:
            self.playCard(move[1])
        elif move[0] == 1:
            self.discardCard(move[1])
        elif move[0] == 2:
            self.giveHint((move[2], move[3], move[4]))
        
        # Next player's turn
        self.legalMoves()
        for card in self.player_hints[self.current_player_turn]:
            # Increment the time the card has been in the player's hand
            card[2] += 1
        self.current_player_turn = ((self.current_player_turn + 1) 
                                                        % self.num_players)
        
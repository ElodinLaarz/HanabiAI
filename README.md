# HanabiAI
A machine-learning AI that learns to play the card game Hanabi

# What is Hanabi?
[Hanabi](https://en.wikipedia.org/wiki/Hanabi_(card_game)) is a card game where each player is dealt a hand of cards that only the **other** players can see!
The cards have a number and a color (e.g. a Green 3 or a Red 1). You win once the deck is out of cards and your score is the number of cards you were succesfully able to play.

On your turn, you have the option to either play a card from your hand, discard a card from your hand, or give someone a hint. A hint consists of saying a number or color
and then marking **all** the cards in the player's hand that are of that color/number.
There are limited hints, limited cards in the deck, and if you try to play a card and it's unplayable a firework goes off! If enough fireworks go off, you get a score of 0!

# How does it work?
The program useses a genetic algorithm to determine when to play/discard/give a hint. In a given generation of AI players, they are then randomly paired up with partners and their end score determines which genes get passed on to future generations!

# Are the AI players it any good?
I've gotten AI players that have scored an average of 18 points over 10 games. (In the standard game in which maximum score is 25.)

# How do I run this?
Most of the project is broken in Jupyter notebooks with examples of how to run it; clone and check it out if you're interested!

# There are no weights in the weights folder!
You'll have to generate some yourself, then: get to it!

# Can I just use this to play Hanabi?
There is a fully-functional implementation of Hanabi that you can play, yes. You can even change the number of hints/fireworks/number of cards for added challenge. Although, it's entirely text-based and not nearly visually appealing as the real card game, which I fully endorse.

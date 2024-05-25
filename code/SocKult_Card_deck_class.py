import random

class CardDeck:
    def __init__(self, number_of_decks):
        self.number_of_decks = number_of_decks
        self.cards = None

    def create_deck(self):
        self.cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [j for j in self.cards for i in range(4)]
        self.cards = [j for j in self.cards for i in range(self.number_of_decks)]
        random.shuffle(self.cards)

    def deal_cards(self):
        return [self.cards.pop(0), self.cards.pop(0)]

    def draw_card(self):
        return self.cards.pop(0)

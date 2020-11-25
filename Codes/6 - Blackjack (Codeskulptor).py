# Blackjack simplificado (sem apostas, split, double, surrender)
# Dealer hit enquanto tem mão com valor <= 16.

# ---------- IMPORTS ---------- #

import simplegui
import random


# ---------- GLOBAL VARIABLES ---------- #

WINDOW_TITLE = 'Blackjack'
WIDTH = 600
HEIGHT = 600

in_play = False  # True = mão em andamento, False = mão finalizada
win = loss = tie = 0
message = ''
computer_value = ''

SUITS = ['C', 'S', 'H', 'D']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
VALUES = {'A':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':10, 'Q':10, 'K':10}


# ---------- LOAD DE ARQUIVOS ---------- #

# load card sprite - 950x392 - source: jfitz.com
card_images = simplegui.load_image("http://storage.googleapis.com/codeskulptor-assets/cards_jfitz.png")
card_back = simplegui.load_image("http://storage.googleapis.com/codeskulptor-assets/card_jfitz_back.png")    


# ---------- AUXILIARY FUNCTIONS ---------- #

# Desenha um retângulo a partir de coordenadas = (topleft_x, topleft_y, width, height)
def rect(canvas, coord, thickness, color_in, color_out):
    canvas.draw_polygon(((coord[0], coord[1]), 
                         (coord[0] + coord[2], coord[1]), 
                         (coord[0] + coord[2], coord[1] + coord[3]), 
                         (coord[0], coord[1] + coord[3])), 
                         thickness, color_out, color_in)


# ---------- CLASSES ---------- #

class Card:
    card_size = (72, 96)
    card_back_size = (72, 96)

    def __init__(self, rank, suit):
        if (suit in SUITS) and (rank in RANKS):
            self.suit = suit
            self.rank = rank
        else:
            self.suit = None
            self.rank = None
            print('Invalid card: ', suit, rank)

    def get_rank(self):
        return self.rank
                     
    def get_suit(self):
        return self.suit

    def __str__(self):
        return self.rank + self.suit

    # Desenha uma carta na posição pos (com referência em top_left)
    def draw(self, canvas, pos):
        i = RANKS.index(self.rank)
        j = SUITS.index(self.suit)
        card_pos_tile = (Card.card_size[0] * (0.5 + i),
                         Card.card_size[1] * (0.5 + j))
        card_pos_canvas = [pos[0] + Card.card_size[0] // 2, 
                           pos[1] + Card.card_size[1] // 2]

        # Parâmetros: imagem, (centro)_imag, (width, height)_imag, 
        #             (centro)_canvas, (width, height)_canvas
        canvas.draw_image(card_images, card_pos_tile, Card.card_size, 
                          card_pos_canvas, Card.card_size)

    def draw_back(self, canvas, pos, color='blue'):
        colors = {'blue':0, 'red':1}
        card_pos_tile = (Card.card_back_size[0] * (0.5 + colors[color]), 
                         Card.card_back_size[1] * 0.5)
        card_pos_canvas = [pos[0] + Card.card_size[0] // 2, 
                           pos[1] + Card.card_size[1] // 2]

        canvas.draw_image(card_back, card_pos_tile, Card.card_back_size, 
                          card_pos_canvas, Card.card_back_size)


class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        total = 0
        ace = False # Ás na mão que conta como 11 (só pode existir um)
        for card in self.cards:                
            total += VALUES[card.get_rank()]
            if card.get_rank() == 'A':
                if total + 10 <= 21:
                    total = total + 10
                    ace = True
            if total > 21 and ace:
                    total -= 10
                    ace = False  # Sem essa linha AAATT valeria 13 e não 23.
        return total

    def busted(self):
        return self.get_value() > 21

    def draw(self, canvas, pos):
        for i, card in enumerate(self.cards):
            card.draw(canvas, pos)
            pos = list(pos)

            # Desenha 6 cartas lado a lado e avança para a próxima linha
            pos[0] = (pos[0] + Card.card_size[0] + 15) % (6*Card.card_size[0] + 6*15)
            if i == 5:  # Desenha a 6a. carta normalmente com pos[1]. A seguir
                        # atualiza pos[1] para mudar de linha
                pos[1] = pos[1] + Card.card_size[1] + 5

    def __str__(self):
        string = ''
        for card in self.cards:
            string += ', ' + str(card)
        return 'Hand contains:' + string[1:]


class Deck:
    def __init__(self):
        self.deck = [Card(rank, suit) for suit in SUITS for rank in RANKS]

    def shuffle(self):
        random.shuffle(self.deck)

    # Com pop() a última carta é retirada (imagine que o baralho está empilhado
    # normalmente (a carta do topo, à mostra, é o início da lista). Aí você vira ele de cabeça
    # pra baixo e começa a retirar cartas do topo. Esse topo na verdade é o fim da lista.
    def deal_card(self):
        return self.deck.pop()

    def __str__(self):
        string = ''
        for card in self.deck:
            string += ', ' + str(card)
        return 'Deck contains:' + string[1:]


# ---------- EVENT HANDLER FUNCTIONS ---------- #

def deal():
    global in_play, message, loss
    global player_hand, computer_hand
    global deck

    message = 'Hit or stand?'
    player_hand = Hand()
    computer_hand = Hand()
    deck = Deck()
    deck.shuffle()
    
    for i in range(2):
        player_hand.add_card(deck.deal_card())
        computer_hand.add_card(deck.deal_card())

    if in_play:
        loss += 1
    in_play = True

def hit():
    global in_play, loss, message
    global player_hand, computer_hand
    if in_play and not player_hand.busted():
        player_hand.add_card(deck.deal_card())
        if player_hand.busted():
            message = 'You busted! New deal?'
            loss += 1; in_play = False

def stand():
    global in_play, message, win, loss, tie
    global player_hand, computer_hand
    if in_play:
        while computer_hand.get_value() <= 16:
            computer_hand.add_card(deck.deal_card())

        if computer_hand.busted():
            message = 'Dealer busts! You won! New deal?'
            win += 1; in_play = False
        else:
            if player_hand.get_value() > computer_hand.get_value():
                message = 'You win! New deal?'
                win += 1; in_play = False
            elif player_hand.get_value() == computer_hand.get_value():
                message = "It's a tie! New deal?"
                tie += 1; in_play = False
            else:
                message = 'Dealer wins! You lost. New deal?'
                loss +=1; in_play = False


# ---------- DRAW HANDLER FUNCTION ---------- #

def draw(canvas):
    global computer_value

    computer_hand.draw(canvas, (60, 150))
    player_hand.draw(canvas, (60, 395))

    rect(canvas, (55,68, frame.get_canvas_textwidth(message, 24)+10, 30), 2, 'Green', 'Silver')
    canvas.draw_text(message, (60,90), 24, 'White')

    canvas.draw_text('Blackjack', (225,45), 38, 'White')
    canvas.draw_text("Dealer's Hand" + '     Value: ' + str(computer_value), (60,135), 18, 'White')
    canvas.draw_text("Player's Hand" + '     Value: ' + str(player_hand.get_value()), (60,380), 18, 'White')
    canvas.draw_text('Win/Loss/Tie: ' + str(win)+'/'+str(loss)+'/'+str(tie), (402,588), 20, 'White')
    if in_play:
        computer_hand.cards[0].draw_back(canvas, (60, 150), 'red')
        if computer_hand.cards[1].get_rank() == 'A':
            computer_value = 11
        else:
            computer_value = VALUES[computer_hand.cards[1].get_rank()]
    else:
        computer_value = computer_hand.get_value()


# ---------- CREATE FRAME ---------- #

frame = simplegui.create_frame(WINDOW_TITLE, WIDTH, HEIGHT)
frame.set_canvas_background("Green")


# ---------- REGISTER HANDLERS ---------- #

frame.add_button("Deal", deal, 200)
frame.add_button("Hit",  hit, 200)
frame.add_button("Stand", stand, 200)
frame.set_draw_handler(draw)


# ---------- OTHER GLOBALS, OBJECTS CREATION ---------- #

deck = Deck()
player_hand = Hand()
computer_hand = Hand()
deal()

# ------------ FRAME INITIALIZATION ------------ #

frame.start()


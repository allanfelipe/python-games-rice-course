# ---------- IMPORTS ---------- #

import simplegui
import random


# ---------- GLOBAL VARIABLES ---------- #

WINDOW_TITLE = 'Memory'
WIDTH = 800
HEIGHT = 100

state = 0  # 0 = início, 1 = uma carta exposta, 2 = duas cartas expostas
flip = 0  # 1 = última dupla exposta tem 2 números iguais, 0 = diferentes
aux_cards = [0]*4  # Posições 0 e 1: índice das 2 últimas cartas que viraram
                   # Posições 2 e 3: auxiliares
turns = 0


# ---------- AUXILIARY FUNCTIONS ---------- #

# Retângulo com borda e coordenadas = (topleft_x, topleft_y, width, height)
def rect(surface, coord, thickness, color_in, color_out):
    surface.draw_polygon(((coord[0],coord[1]), 
                          (coord[0]+coord[2],coord[1]),
                          (coord[0]+coord[2],coord[1]+coord[3]), 
                          (coord[0],coord[1]+coord[3])), 
                         thickness, color_out, color_in)

def create_cards():
    cards = []
    x = list(range(16))
    random.shuffle(x)
    for n, pos in zip(x, list(range(16))):
        cards.append(Card(n%8, pos))
    return cards


# ---------- CLASSES ---------- #

class Card:
    def __init__(self, number, position):
        self.number = number
        self.exposed = False
        self.position = position*50

    def draw(self, surface):
        if self.exposed == True:
            rect(surface, (self.position, 0, WIDTH//16, HEIGHT), 1, 'Green', 'Black')
            surface.draw_text(str(self.number + 1), (self.position + 17, HEIGHT//2 + 12), 38, 'White')
        else:
            rect(surface, (self.position, 0, WIDTH//16, HEIGHT), 1, 'rgb(139,100,15)', 'Black')            


# ---------- EVENT HANDLER FUNCTIONS ---------- #

def new_game():
    global state, flip, aux_cards, turns, cards
    state = flip = 0
    aux_cards = [0]*4
    turns = 0
    cards = create_cards()


def mouseclick(pos):
    global state, turns, flip, cards
    x, y = pos
    for n in range(16):
        if x > cards[n].position and x < cards[n].position + 50:
            if cards[n].exposed == False:
                cards[n].exposed = True
                state = (state % 2) + 1
                turns += 1
                if state == 1:
                    aux_cards[0] = cards[n].position // 50
                elif state == 2:
                    aux_cards[1] = cards[n].position // 50
    
    if state == 2:
        aux_cards[2] = aux_cards[0]
        aux_cards[3] = aux_cards[1]
        if cards[aux_cards[0]].number != cards[aux_cards[1]].number:
            flip = 1
    elif state == 1 and flip == 1:
        cards[aux_cards[2]].exposed = False
        cards[aux_cards[3]].exposed = False
        flip = 0


# ---------- DRAW HANDLER FUNCTION ---------- #

def draw(canvas):
    for n in range(16):
        cards[n].draw(canvas)
    label.set_text('Turns = ' + str(turns//2))


# ---------- CREATE FRAME ---------- #

frame = simplegui.create_frame(WINDOW_TITLE, WIDTH, HEIGHT)


# ---------- REGISTER HANDLERS ---------- #

frame.add_button('Reset', new_game)
label = frame.add_label('Turns = 0')
frame.set_mouseclick_handler(mouseclick)
frame.set_draw_handler(draw)


# ---------- OTHER GLOBALS, OBJECTS CREATION ---------- #

new_game()


# ------------ FRAME INITIALIZATION ------------ #

frame.start()



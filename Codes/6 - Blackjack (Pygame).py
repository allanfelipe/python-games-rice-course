#!/usr/bin/env python3

# Blackjack simplificado (sem apostas, split, double, surrender)
# Dealer hit enquanto tem mão com valor <= 16

# ---------- IMPORTS ---------- #

import os, sys
import pygame as pg
from pygame.locals import *
import random


# ---------- GLOBAL VARIABLES ---------- #

WINDOW_TITLE = 'Blackjack'
WIDTH = 600
HEIGHT = 600
FPS = 30

white = pg.Color(255, 255, 255)
light_grey = pg.Color(220, 220, 220)
black = pg.Color(0, 0, 0)
green = pg.Color(39, 119, 35)
orange = pg.Color(205, 133, 70)

in_play = False  # True = mão em andamento, False = mão finalizada
game_state = 0  # 0 = Splash Screen, 1 = Game
message = ''
computer_value = ''

SUITS = ['C', 'S', 'H', 'D']
RANKS = ['A', '2', '3', '4', '5','6', '7', '8', '9', 'T', 'J', 'Q', 'K']
VALUES = {'A':1, '2':2, '3':3, '4':4, '5':5,'6':6, '7':7, '8':8, '9':9, 
          'T':10, 'J':10, 'Q':10, 'K':10}


# ---------- LOAD DE ARQUIVOS ---------- #

pg.init()

# cards - source: jfitz.com
cards_tile = pg.image.load('data/images/cards_jfitz.png')
cards_back = pg.image.load('data/images/card_jfitz_back.png')
# background - source: pexels.com
background = pg.image.load('data/images/Splash-Pexel.png')

font_title1 = pg.font.Font('data/fonts/Casino3DLines.ttf', 98)
font_title2 = pg.font.Font('data/fonts/Casino.ttf', 25)
font1 = pg.font.Font('data/fonts/LiberationSerif-Regular.ttf', 28)  # Message e buttons
font2 = pg.font.Font('data/fonts/LiberationSerif-Regular.ttf', 20)  # Score
font3 = pg.font.Font('data/fonts/LiberationSerif-Regular.ttf', 18)  # Valores das mãos


# ---------- INITIALIZE SCREEN ---------- #

canvas = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption(WINDOW_TITLE)


# ---------- AUXILIARY FUNCTIONS ---------- #

# Desenha um retângulo com borda
def rectangle_ring(surface, color_int, color_ext, rect, thickness):
    rect = pg.Rect(rect)
    pg.draw.rect(surface, color_ext, rect)
    pg.draw.rect(surface, color_int, rect.inflate(-thickness, -thickness))

def draw_scene(surface):
    global computer_value
    title_top = font_title2.render('Blackjack', True, white)
    surface.blit(title_top, (WIDTH // 2 - title_top.get_width() // 2, 15 ))
    dealer_string = font3.render("Dealer's Hand" + '      Value: ' + str(computer_value), True, white)
    canvas.blit(dealer_string, (60, 120))
    player_string = font3.render("Player's Hand" + '      Value: ' + str(player_hand.get_value()), True, white)
    canvas.blit(player_string, (60, 355))
    message_string = font1.render(message, True, white)
    rectangle_ring(surface, green, white, (55, 65, message_string.get_width() + 10, message_string.get_height()), 2)
    canvas.blit(message_string, (60, 65))


# ---------- CLASSES ---------- #

class Button:
    def __init__ (self, rect, color, font, text='', text_color=(255,255,255)):
        self.rect = pg.Rect(rect)  # rect = (topleft_x, topleft_y, width, height)
        self.color = color
        self.original_color = color
        self.font = font
        self.text = text
        self.text_color = text_color
        self.clicked = False

    def handle_events(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
        if self.clicked == True:
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                self.clicked = False

        # Quando botão é clicado, sua cor fica um pouco mais escura.
        if self.clicked == False:
            self.color = self.original_color
        else:
            factor = 0.85
            self.color = (int(factor*self.original_color[0]),int(factor*self.original_color[1]),int(factor*self.original_color[2]), self.original_color[3])

    def draw_text(self):
        text_surface = font1.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect()
        canvas.blit(text_surface,
                    (self.rect[0] + self.rect[2]/2 - text_rect.width/2,
                     self.rect[1] + self.rect[3]/2 - text_rect.height/2))

    def draw(self, surface):
        pg.draw.rect(surface, self.color, self.rect)
        self.draw_text()


class Card:
    card_size = (72, 96)
    card_back_size = (72, 96)

    def __init__(self, rank, suit):
        if (suit in SUITS) and (rank in RANKS):
            self.rank = rank
            self.suit = suit
        else:
            self.rank = None
            self.suit = None
            print('Invalid card: ', suit, rank)

    def get_rank(self):
        return self.rank

    def get_suit(self):
        return self.suit

    def __str__(self):
        return self.rank + self.suit

    # Desenha uma carta na posição pos (com referência em top_left)
    def draw(self, surface, pos):
        i = RANKS.index(self.rank)
        j = SUITS.index(self.suit)
        card_pos_tile = (i * Card.card_size[0], j * Card.card_size[1])

        # Parâmetros: imagem, (topleft)_surface, (rect)_imag
        surface.blit(cards_tile, pos, (card_pos_tile[0], card_pos_tile[1],
                     Card.card_size[0], Card.card_size[1]))

    def draw_back(self, surface, pos, color='blue'):
        colors = {'blue':0, 'red':1}
        card_pos_tile = (colors[color] * Card.card_back_size[0], 0)
        surface.blit(cards_back, pos, (card_pos_tile[0], card_pos_tile[1],
                     Card.card_back_size[0], Card.card_back_size[1]))


class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        total = 0
        ace = False  # Ás na mão que conta como 11 (só pode existir um)
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

    def draw(self, surface, pos):
        for i, card in enumerate(self.cards):
            card.draw(surface, pos)
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
    # normalmente (a carta do topo, à mostra, é o início da lista). Aí você vira ele de
    # cabeça pra baixo e começa a retirar cartas do topo. Esse topo na verdade é o fim da lista.
    def deal_card(self):
        return self.deck.pop()

    def __str__(self):
        string = ''
        for card in self.deck:
            string += ', ' + str(card)
        return 'Deck contains:' + string[1:]


class SplashScreen:
    def draw(surface):
       surface.blit(background, (0, 0))
       title = font_title1.render('Blackjack', True, white)
       surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 45))
       Button_Play.draw(canvas)

    def handle_events(event):
        Button_Play.handle_events(event)
        if Button_Play.clicked == True:
            deal()

class Score:
   def __init__(self):
       self.win = 0
       self.loss = 0
       self.tie = 0

   def draw(self, surface):
       score = font2.render('Win/Loss/Tie: ' + str(self.win) + '/' + str(self.loss) 
                             + '/' + str(self.tie), True, white)
       surface.blit(score, (402, 568))


# ---------- EVENT HANDLER FUNCTIONS ---------- #

def deal():
    global in_play, game_state, message
    global player_hand, computer_hand, deck

    message = 'Hit or stand?'
    game_state = 1
    player_hand = Hand()
    computer_hand = Hand()
    deck = Deck()
    deck.shuffle()

    for i in range(2):
        player_hand.add_card(deck.deal_card())
        computer_hand.add_card(deck.deal_card())

    if in_play:
        score.loss += 1
    in_play = True

def hit():
    global in_play, message
    global player_hand, computer_hand
    if in_play and not player_hand.busted():
        player_hand.add_card(deck.deal_card())
        if player_hand.busted():
            message = 'You busted! New deal?'
            score.loss += 1; in_play = False

def stand():
    global in_play, message
    global player_hand, computer_hand
    if in_play:
        while computer_hand.get_value() <= 16:
            computer_hand.add_card(deck.deal_card())

        if computer_hand.busted():
            message = 'Dealer busts! You won! New deal?'
            score.win += 1; in_play = False
        else:
            if player_hand.get_value() > computer_hand.get_value():
                message = 'You win! New deal?'
                score.win += 1; in_play = False
            elif player_hand.get_value() == computer_hand.get_value():
                message = "It's a tie! New deal?"
                score.tie += 1; in_play = False
            else:
                message = 'Dealer wins! You lost. New deal?'
                score.loss += 1; in_play = False

def event_handlers():
    global game_state
    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit(); sys.exit()

        elif event.type == pg.KEYDOWN:
            if event.key == K_ESCAPE:
                pg.quit(); sys.exit()

        if game_state == 0:
            SplashScreen.handle_events(event)

        elif game_state == 1:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                if Button_Deal.rect.collidepoint(mouse_pos):
                    deal()
                elif Button_Hit.rect.collidepoint(mouse_pos):
                    hit()
                elif Button_Stand.rect.collidepoint(mouse_pos):
                    stand()

            Button_Deal.handle_events(event)
            Button_Hit.handle_events(event)
            Button_Stand.handle_events(event)


# ---------- DRAW HANDLER FUNCTION ---------- #

def draw_handler(canvas):
    global computer_value

    if game_state == 0:
        SplashScreen.draw(canvas)

    elif game_state == 1:
        canvas.fill(green)
        draw_scene(canvas)

        Button_Deal.draw(canvas)
        Button_Hit.draw(canvas)
        Button_Stand.draw(canvas)

        computer_hand.draw(canvas, (60, 150))
        player_hand.draw(canvas, (60, 385))
        score.draw(canvas)

        if in_play:
            computer_hand.cards[0].draw_back(canvas, (60, 150), 'red')
            if computer_hand.cards[1].get_rank() == 'A':
                computer_value = 11
            else:
                computer_value = VALUES[computer_hand.cards[1].get_rank()]
        else:
            computer_value = computer_hand.get_value()

    pg.display.update()


# ------------ OTHER GLOBALS, OBJECTS CREATION ------------ #

Button_Play = Button((220,370,90,30), light_grey, font1, 'Play!', black)
Button_Deal = Button((470,20,110,30), orange, font1, 'Deal', white)
Button_Hit = Button((470,75,110,30), orange, font1, 'Hit', white)
Button_Stand = Button((470,115,110,30), orange, font1, 'Stand', white)

deck = Deck()
player_hand = Hand()
computer_hand = Hand()
score = Score()


# ------------ TIMER INITIALIZATION / MAIN LOOP ------------ #

def main():
    clock = pg.time.Clock()

    while True:
        event_handlers()
        draw_handler(canvas)
        clock.tick(FPS)


if __name__ == '__main__':
    main()











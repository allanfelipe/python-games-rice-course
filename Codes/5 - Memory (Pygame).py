#!/usr/bin/env python3

# ---------- IMPORTS ---------- #

import os, sys
import pygame as pg
from pygame.locals import *
from pygame import gfxdraw
import random


# ---------- GLOBAL VARIABLES ---------- #

WINDOW_TITLE = 'Memory'
WIDTH_TOTAL = 850
WIDTH = 800
HEIGHT = 100
FPS = 10

white = pg.Color(255, 255, 255)
black = pg.Color(0, 0, 0)
green = pg.Color(39, 119, 35)
brown = pg.Color(139, 100, 15)

game_state = 1  # 1 = jogo em andamento, 0 = fim de jogo
state = 0  # 0 = início, 1 = uma carta exposta, 2 = duas cartas expostas
flip = 0  # 1 = última dupla exposta tem 2 números iguais, 0 = diferentes
aux_cards = [0]*4  # Posições 0 e 1: índice das 2 últimas cartas que viraram
                   # Posições 2 e 3: auxiliares

# ---------- LOAD DE ARQUIVOS ---------- #

pg.init()

font1 = pg.font.Font('data/fonts/Junegull.ttf', 48)
font2 = pg.font.Font('data/fonts/LiberationSerif-Regular.ttf', 16)
font3 = pg.font.Font('data/fonts/LiberationSerif-Regular.ttf', 44)


# ---------- INITIALIZE SCREEN ---------- #

canvas = pg.display.set_mode((WIDTH_TOTAL, HEIGHT))
pg.display.set_caption(WINDOW_TITLE)


# ---------- AUXILIARY FUNCTIONS ---------- #

# Desenha um retângulo com borda
def rectangle_ring(surface, color_int, color_ext, rect, thickness):
    rect = pg.Rect(rect)
    pg.draw.rect(surface, color_ext, rect)
    pg.draw.rect(surface, color_int, rect.inflate(-thickness, -thickness))

# Cria as 16 cartas embaralhadas
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
        self.position = position * 50
        self.exposed = False
        self.text = font1.render(str(self.number + 1), True, black)
        self.rect = pg.Rect(self.position, 0, WIDTH//16, HEIGHT)

    def handle_events(self, event):
        global state
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.exposed == False:
                    self.exposed = True
                    state = (state % 2) + 1
                    score.turns += 1
                    if state == 1:
                        aux_cards[0] = self.position // 50
                    elif state == 2:
                        aux_cards[1] = self.position // 50

    def draw(self, surface):
        if self.exposed == True:
            rectangle_ring(surface, green, black, self.rect, 2)
            surface.blit(self.text,
                         (self.rect[0]+self.rect[2]//2-self.text.get_width()//2,
                          self.rect[3]//2-self.text.get_height()//2))
        else:
            rectangle_ring(surface, brown, black, self.rect, 2)


class Score:
   def __init__(self):
       self.turns = 0

   def draw(self, surface):
       title_r = font2.render('Turns', True, black)
       turn_r = font3.render(str(self.turns//2), True, black)
       surface.blit(title_r, (WIDTH_TOTAL - 1.2 * title_r.get_width(),
                    HEIGHT - 4.5 * title_r.get_height()))
       if (self.turns//2) <= 9:
           surface.blit(turn_r, (WIDTH_TOTAL - 1.6 * turn_r.get_width(),
                        HEIGHT - 1.3 * turn_r.get_height()))
       else:
           surface.blit(turn_r, (WIDTH_TOTAL - 1.1 * turn_r.get_width(),
                        HEIGHT - 1.3 * turn_r.get_height()))


class Game:
    def __init__ (self, Score, Cards):
        self.Score = Score
        self.Cards = Cards

    def new_game(self):
        global cards, game_state, state, flip, aux_cards
        game_state = 1
        state = flip = 0
        aux_cards = [0]*4
        self.Score.turns = 0
        self.Cards = create_cards()

    def update(self):
        global state, flip, game_state

        if state == 2:
            aux_cards[2] = aux_cards[0]
            aux_cards[3] = aux_cards[1]
            if self.Cards[aux_cards[0]].number != self.Cards[aux_cards[1]].number:
                flip = 1

        elif state == 1 and flip == 1:
            self.Cards[aux_cards[2]].exposed = False
            self.Cards[aux_cards[3]].exposed = False
            flip = 0

        if False not in [card.exposed for card in self.Cards]:
            game_state = 0

    
class end_of_game:
   def draw(surface):
       game_over = font2.render('Game over. Play again? (y/n)', True, white)
       surface.blit(game_over, (WIDTH/2 - game_over.get_width()//2, HEIGHT/1.3))

   def event_handler(event):
       if event.key == pg.K_y:
           game.new_game()
       elif event.key == pg.K_n:
           pg.quit(); sys.exit()


# ---------- EVENT HANDLER FUNCTION ---------- #

def event_handlers():
    global game_state
    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit(); sys.exit()

        elif event.type == pg.KEYDOWN:
            if event.key == K_ESCAPE:
                pg.quit(); sys.exit()

            elif game_state == 0:
                end_of_game.event_handler(event)

        for card in game.Cards:
            card.handle_events(event)


# ---------- DRAW HANDLER FUNCTION ---------- #

def draw_handler(canvas):
    global game_state

    canvas.fill(white)

    if game_state == 1:
        game.update()
    elif game_state == 0:
        end_of_game.draw(canvas)

    for card in game.Cards:
        card.draw(canvas)
    score.draw(canvas)

    pg.display.update()


# ------- OTHER GLOBALS, INITIALIZATIONS, OBJECTS CREATION ------- #

cards = create_cards()
score = Score()
game = Game(score, cards)


# ------------ TIMER INITIALIZATION / MAIN LOOP ------------ #

def main():
    clock = pg.time.Clock()
    while True:
        event_handlers()
        draw_handler(canvas)
        clock.tick(FPS)


if __name__ == '__main__':
    main()
    


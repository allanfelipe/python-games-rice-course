#!/usr/bin/env python3

# ---------- IMPORTS ---------- #

import os, sys
import pygame as pg
from pygame.locals import *
import random


# ---------- GLOBAL VARIABLES ---------- #

WINDOW_TITLE = 'Stopwatch'
WIDTH = 380
HEIGHT = 240
FPS = 30

black = pg.Color(0, 0, 0)
blue = pg.Color(0, 0, 255)
white = pg.Color(255, 255, 255)
background_light = pg.Color(210,230,235)

TIMER_ID = USEREVENT + 1
TIMER_OFF = 0
interval = 100  # Ticks do timer em ms (100ms = 0.1s)
state = TIMER_OFF

count = 0
score = 0
total = 0


# ---------- LOAD DE ARQUIVOS ---------- #

pg.init()

font1 = pg.font.Font('data/fonts/OpenSans-Regular.ttf', 20)
font2 = pg.font.Font('data/fonts/OpenSans-Regular.ttf', 48)


# ---------- INITIALIZE SCREEN ---------- #

canvas = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption(WINDOW_TITLE)


# ---------- CLASSES ---------- #

class Button:
    def __init__ (self, rect, color, text='', text_color=white):
        self.rect = pg.Rect(rect)  # rect = (topleft_x, topleft_y, width, height)
        self.color = color
        self.original_color = color
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

        # Quando botão não está clicado, mantém a cor original. Quando está
        # clicado (mesmo quando arrasta o mouse enquanto mantém clicado), escurece
        # a cor.
        if self.clicked == False:
            self.color = self.original_color
        else:
            factor = 0.85
            self.color = (int(factor*self.original_color[0]),
                          int(factor*self.original_color[1]),
                          int(factor*self.original_color[2]),
                          self.original_color[3])

    def draw_text(self):
        text_surface = font1.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect()
        canvas.blit(text_surface, 
                    (self.rect[0] + self.rect[2]/2 - text_rect.width/2,
                     self.rect[1] + self.rect[3]/2 - text_rect.height/2))

    def draw(self, surface):
        pg.draw.rect(surface, self.color, self.rect)
        self.draw_text()


# ---------- AUXILIARY FUNCTIONS ---------- #

def quit():
    pg.quit()
    sys.exit()

def format(number):
    tenths = number % 10
    seconds = (number // 10) % 60
    minutes = number // (10 * 60)
    D = tenths
    B = seconds // 10
    C = seconds % 10
    A = minutes
    return str(A) + ':' + str(B) + str(C) + '.' + str(D)


# ---------- EVENT HANDLER FUNCTIONS ---------- #

def timer_handler():
    global count
    count += 1

def event_handlers():
    global count, score, total, state

    for event in pg.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                quit()
        elif event.type == QUIT:
            quit()

        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pg.mouse.get_pos()
            if Button_Start.rect.collidepoint(mouse_pos):
                state = interval
                pg.time.set_timer(TIMER_ID, state)
            elif Button_Stop.rect.collidepoint(mouse_pos):
            # Impede ganhar ponto ao clicar no stop quando a contagem está parada
                if state != TIMER_OFF:
                    if int(format(count)[-1]) == 0:
                        score += 1
                    total += 1
                    state = TIMER_OFF
                pg.time.set_timer(TIMER_ID, state)
            elif Button_Reset.rect.collidepoint(mouse_pos):
                state = TIMER_OFF
                pg.time.set_timer(TIMER_ID, state)
                count = score = total = 0

        elif event.type == TIMER_ID:
            timer_handler()

        Button_Start.handle_events(event)
        Button_Stop.handle_events(event)
        Button_Reset.handle_events(event)


# ---------- DRAW HANDLER FUNCTION ---------- #

def draw():
    canvas.fill(background_light)

    Button_Start.draw(canvas)
    Button_Stop.draw(canvas)
    Button_Reset.draw(canvas)

    text_stopwatch = font2.render(format(count), True, black)
    canvas.blit(text_stopwatch, (WIDTH/2 - text_stopwatch.get_width()/2, 100))

    text_score = font1.render(str(score) + ' / ' + str(total), True, blue)
    canvas.blit(text_score, (310, 200))

    pg.display.update()


# ------- OTHER GLOBALS, OBJECTS CREATION ------- #

Button_Start = Button((30,25,100,30), blue, 'Start', white)
Button_Stop = Button((140,25,100,30), blue, 'Stop', white)
Button_Reset = Button((250,25,100,30), blue, 'Reset', white)


# ------------ TIMER INITIALIZATION / MAIN LOOP ------------ #

def main():
    clock = pg.time.Clock()
    while True:
        event_handlers()
        draw()
        clock.tick(FPS)


if __name__ == '__main__':
    main()



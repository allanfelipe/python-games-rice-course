#!/usr/bin/env python3

# ---------- IMPORTS ---------- #

import os, sys
import pygame as pg
from pygame.locals import *
import math
import random


# ---------- GLOBAL VARIABLES ---------- #

WINDOW_TITLE = 'Adivinhe o Número'
WIDTH = 400
HEIGHT = 300
FPS = 30

black = pg.Color(0, 0, 0)
blue = pg.Color(0, 0, 255)
white = pg.Color(255, 255, 255)
light_blue = pg.Color(141, 182, 205)
dark_blue = pg.Color(28, 134, 238)
background_light = pg.Color(216,233,255)

n_max = 99
secret_number = 0
remaining = 0

text1 = text2 = text3 = ''


# ---------- LOAD DE ARQUIVOS ---------- #

pg.init()

font1 = pg.font.Font('data/fonts/Roboto-Regular.ttf', 15)


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


class InputBox:
    def __init__(self, rect, text='', color_inactive=light_blue,
                 color_active=dark_blue):
        self.rect = pg.Rect(rect)  # rect = (topleft_x, topleft_y, width, height)
        self.text = text
        self.color = color_inactive
        self.text_surface = font1.render(text, True, black)
        self.active = False  # Abre a janela sem o foco na caixa de texto
        self.width_original = rect[2]
        self.color_active = color_active
        self.color_inactive = color_inactive

    def handle_events(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # Quando clica na caixa o foco permanece nela e a cor muda.
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.color = self.color_active
            else:
                self.active = False
                self.color = self.color_inactive

        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                    input_guess(self.text)
                    self.text = ''
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    # Se tem até 2 caracteres, dá append em apenas mais 1.
                    if len(self.text) <= 2:
                        self.text += event.unicode
                # Re-renderiza o texto.
                self.text_surface = font1.render(self.text, True, black)

    def draw(self, screen):
        pg.draw.rect(screen, white, self.rect)
        pg.draw.rect(screen, self.color, self.rect, 3)
        screen.blit(self.text_surface, (self.rect.x + 5, self.rect.y + 5))


# ---------- AUXILIARY FUNCTIONS ---------- #

def quit():
    pg.quit()
    sys.exit()

def new_game():
    global secret_number, remaining
    remaining = int(math.ceil(math.log(n_max-1) / math.log(2)))
    secret_number = random.randint(0, n_max)


def input_guess(guess):
    global remaining
    global text1, text2, text3
    if guess.isdigit():
        guess = int(guess)

        text1 = 'Seu palpite foi: ' + str(guess)
        remaining -= 1
        if remaining != 0:
            if guess == secret_number:
                text2 = 'Acertou!! Novo jogo iniciado.'
                text3 = ''
                new_game()
            elif guess < secret_number:
                text2 = 'Tente um número mais alto!'
                text3 = 'Palpites restantes: ' + str(remaining)
            elif guess > secret_number:
                text2 = 'Tente um número mais baixo!'
                text3 = 'Palpites restantes: ' + str(remaining)
     
        elif remaining == 0:
            if guess == secret_number:
                text2 = 'Acertou!! Novo jogo iniciado.'
                text3 = ''
                new_game()
            else:
                text1 = 'Acabaram os palpites!'
                text2 = 'O número oculto era: ' + str(secret_number)
                text3 = 'Novo jogo iniciado.'
                new_game()

    else:
        text1 = 'Valor inválido. Digite novamente'
        text2 = ''


# ---------- EVENT HANDLER FUNCTION ---------- #

def range100():
    global n_max, text1, text2, text3
    n_max = 99
    text1 = text2 = ''
    text3 = 'Novo jogo iniciado.'
    input_box.text = ''
    input_box.text_surface = font1.render(input_box.text, True, black)
    new_game()

def range1000():
    global n_max, text1, text2, text3
    n_max = 999
    text1 = text2 = ''
    text3 = 'Novo jogo iniciado.'
    input_box.text = ''
    input_box.text_surface = font1.render(input_box.text, True, black)
    new_game()


def event_handlers():
    for event in pg.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                quit()
        elif event.type == QUIT:
            quit()

        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pg.mouse.get_pos()
            if Button_100.rect.collidepoint(mouse_pos):
                range100()
            elif Button_1000.rect.collidepoint(mouse_pos):
                range1000()

        Button_100.handle_events(event)
        Button_1000.handle_events(event)
        input_box.handle_events(event)


# ---------- DRAW HANDLER FUNCTION ---------- #

def draw_handler(canvas):
    canvas.fill(background_light)

    Button_100.draw(canvas)
    Button_1000.draw(canvas)
    input_box.draw(canvas)

    input_r = font1.render('Digite seu número aqui:', True, black)
    canvas.blit(input_r, (200,65))
    text1_r = font1.render(text1, True, black)
    canvas.blit(text1_r, (110,165))
    text2_r = font1.render(text2, True, black)
    canvas.blit(text2_r, (110,195))
    text3_r = font1.render(text3, True, black)
    canvas.blit(text3_r, (110,215))

    pg.display.update()


# ------- OTHER GLOBALS, INITIALIZATIONS, OBJECTS CREATION ------- #

Button_100 = Button((25,50,130,32), blue, 'Jogo em [0,100[')
Button_1000 = Button((25,90,130,32), blue, 'Jogo em [0,1000[')
input_box = InputBox((255, 90, 40, 30))

new_game()


# ------------ TIMER INITIALIZATION / MAIN LOOP ------------ #

def main():
    clock = pg.time.Clock()
    while True:
        event_handlers()
        draw_handler(canvas)
        clock.tick(FPS)


if __name__ == '__main__':
    main()



# ---------- IMPORTS ---------- #

import os, sys
import pygame as pg
from pygame.locals import *


# ---------- GLOBAL VARIABLES ---------- #

WINDOW_TITLE = 'What is it you want?'
WIDTH = 640
HEIGHT = 480
FPS = 30

white = pg.Color(255, 255, 255)
black = pg.Color(0, 0, 0)
green = pg.Color(0, 255, 0)
cyan = pg.Color(0, 255, 255)
magenta = pg.Color(255, 0, 255)

count = 0


# ---------- LOAD DE ARQUIVOS ---------- #

pg.init()

font = pg.font.Font('data/fonts/OpenSans-Regular.ttf', 30)


# ---------- INITIALIZE SCREEN ---------- #

canvas = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption(WINDOW_TITLE)


# ---------- AUXILIARY FUNCTIONS/VARIABLES ---------- #

def increment():
    global count
    count += 1


# ---------- EVENT HANDLER FUNCTION ---------- #

def event_handlers():
    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit(); sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pg.quit(); sys.exit()


# ---------- DRAW HANDLER FUNCTION ---------- #

def draw_handler(canvas):

    canvas.fill(black)

    text1 = font.render("We", True, white)
    text2 = font.render("want...", True, green)
    text3 = font.render("a", True, cyan)
    text4 = font.render("shrubbery!", True, magenta)

    increment()
    time = count % 120  # 30 unidades = 1 segundo (update em 30FPS)

    if time < 30:
        canvas.blit(text1, (WIDTH//6, HEIGHT//2.5))
    elif time < 60 and time >= 30:
        canvas.blit(text2, (WIDTH//3, HEIGHT//2.5))
    elif time < 90 and time >= 60:
        canvas.blit(text3, (WIDTH//2, HEIGHT//2.5))
    elif time <= 120 and time >60:
        canvas.blit(text4, (WIDTH//1.5, HEIGHT//2.5))

    pg.display.update()


# ------------ TIMER INITIALIZATION / MAIN LOOP ------------ #

def main():
    clock = pg.time.Clock()
    while True:
        event_handlers()
        draw_handler(canvas)
        clock.tick(FPS)

if __name__ == '__main__':
    main()


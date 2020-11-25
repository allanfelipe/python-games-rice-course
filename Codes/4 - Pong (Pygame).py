#!/usr/bin/env python3

# ---------- IMPORTS ---------- #

import os, sys
import pygame as pg
from pygame.locals import *
from pygame import gfxdraw
import random


# ---------- GLOBAL VARIABLES ---------- #

WINDOW_TITLE = 'Pong'
WIDTH = 640
HEIGHT = 480
FPS = 60

white = pg.Color(255, 255, 255)
black = pg.Color(0, 0, 0)
red = pg.Color(255, 0, 0)

PAD_WIDTH = 20
PAD_HEIGHT = 100
PAD_VEL_INICIAL = 4.0 # Velocidade em unidades de pixels/(1/60s)
V_INCREMENT = 1.1

count = 0
FINAL_SCORE = 3  # Ganha quem chega primeiro a este valor
game_state = 1  # 1 = jogo em andamento, 0 = tela final de fim de jogo


# ---------- LOAD DE ARQUIVOS ---------- #

# Dependendo do sistema, se houver latência no áudio, pode ser necessário 
# mexer em pg.mixer.init ou pg.mixer.pre_init
pg.init()

font1 = pg.font.Font('data/fonts/LiberationSerif-Regular.ttf', 46)
som1 = pg.mixer.Sound('data/sounds/447910__breviceps__plop.wav')
som1.set_volume(0.7)


# ---------- INITIALIZE SCREEN ---------- #

canvas = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption(WINDOW_TITLE)


# ---------- CLASSES ---------- #

class Paddle:
    def __init__(self, pad_width, pad_height, pos, color, key_up, key_down):
        self.pad_width = pad_width
        self.pad_height = pad_height
        self.pos = pos  # Lista [pos[0], pos[1]]
        self.color = color
        self.key_up = key_up
        self.key_down = key_down
        self.vel_inicial = PAD_VEL_INICIAL
        self.vel = 0

    def key_event_press(self, event):
        if event.key == self.key_up:
            self.vel = -self.vel_inicial
        elif event.key == self.key_down:
            self.vel = self.vel_inicial

    def key_event_unpress(self, event):
        if event.key == self.key_up:
            self.vel = 0
        elif event.key == self.key_down:
            self.vel = 0

    def update(self):
        self.pos[1] += self.vel
        if self.pos[1] <= 0:
            self.pos[1] = 0
        elif self.pos[1] >= HEIGHT - self.pad_height:
            self.pos[1] = HEIGHT - self.pad_height

    def draw(self, surface):
        # Retângulo - (topleft_x, topleft_y, width, height)
        pg.draw.rect(surface, self.color, (self.pos[0], self.pos[1], self.pad_width, self.pad_height))


class Ball:
    def __init__(self, pos, radius, color_int, color_ext):
        self.pos = [pos[0], pos[1]]
        self.radius = radius
        self.color_int = color_int
        self.color_ext = color_ext
        self.vel_inicial = [random.randint(120, 240)/FPS,  
                            random.choice([-1, 1]) * random.randint(60, 180)/FPS]
        self.vel = self.vel_inicial[:]  # Faz uma cópia e não referência

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

        # Colisão cima/baixo
        if self.pos[1] <= self.radius:
            self.vel[1] = -self.vel[1]
        if self.pos[1] >= HEIGHT-1 - self.radius:
            self.vel[1] = -self.vel[1]

        # Colisão esquerda/direita (na linha)
        if self.pos[0] <= PAD_WIDTH + self.radius:
            self.vel[0] = -self.vel[0]
        if self.pos[0] >= WIDTH-1 - PAD_WIDTH - self.radius:
            self.vel[0] = -self.vel[0]

    def draw(self, surface):
    # Contornando o fato de que não tem função pronta para anel antialiased:
    # desenha o círculo preenchido externo e depois o interno (Pra ficar melhor
    # definido ainda precisa desenhar a linha externa além do círculo preenchido)
        gfxdraw.aacircle(surface, int(self.pos[0]), int(self.pos[1]), 
                         self.radius, self.color_ext)
        gfxdraw.filled_circle(surface, int(self.pos[0]), int(self.pos[1]),
                              self.radius, self.color_ext)

        gfxdraw.aacircle(surface, int(self.pos[0]), int(self.pos[1]),
                         self.radius-2, self.color_int)
        gfxdraw.filled_circle(surface, int(self.pos[0]), int(self.pos[1]),
                              self.radius-2, self.color_int)


class Game:
    def __init__(self, Score, Ball, Paddle1, Paddle2):
        self.Score = Score
        self.Ball = Ball
        self.Paddle1 = Paddle1
        self.Paddle2 = Paddle2

    # Zera o score, coloca os paddles no centro da tela e inicia lançando 
    # uma bola com direção aleatória.
    def new_game(self):
        global game_state
        game_state = 1
        self.Score.score_l = 0
        self.Score.score_r = 0
        self.Paddle1.pos[1] = self.Paddle2.pos[1] = (HEIGHT-1)/2 - PAD_HEIGHT/2
        spawn_ball(self.Ball, self.Score, random.choice([1, -1]), 
                   self.Paddle1, self.Paddle2)

    # Quando a bola chega na linha, caso não encoste no paddle, score é 
    # atualizado e uma bola é lançada.
    def update(self):
        if collision_l(self.Paddle1, self.Ball) == False:
            self.Score.score_r += 1
            spawn_ball(self.Ball, self.Score, 1, self.Paddle1, self.Paddle2)
        if collision_r(self.Paddle2, self.Ball) == False:
            score.score_l += 1
            spawn_ball(self.Ball, self.Score, -1, self.Paddle1, self.Paddle2)


class EndOfGame:
    def draw(surface):
        global count
        count += 1
        text1 = font1.render('Game', True, red)
        text2 = font1.render('Over', True, red)

        if count % 60 < 30:
            surface.blit(text1, (WIDTH/2 - text1.get_width() - WIDTH/30, HEIGHT/5))
        else:
            surface.blit(text2, (WIDTH/2 + WIDTH/30, HEIGHT/5))

        text3 = font1.render('Play again? (y/n)', True, white)
        surface.blit(text3, (WIDTH/2 - text3.get_width()//2, HEIGHT/1.3))

    def event_handler(event):
        if event.key == pg.K_y:
            game.new_game()
        elif event.key == pg.K_n:
            pg.quit(); sys.exit()


class Score:
    def __init__(self):
        self.score_l = 0
        self.score_r = 0

    def draw(self, surface):
        score_l = font1.render(str(self.score_l), True, white)
        score_r = font1.render(str(self.score_r), True, white)
        surface.blit(score_l, (WIDTH/2 - score_l.get_width()/2 - WIDTH/4,
                     HEIGHT/2 - score_l.get_height()/2))
        surface.blit(score_r, (WIDTH/2 - score_r.get_width()/2 + WIDTH/4, 
                     HEIGHT/2 - score_r.get_height()/2))


# ---------- AUXILIARY FUNCTIONS ---------- #

def collision_l(Paddle, Ball):
    # Quando a bola está na linha da esquerda, verifica se colidiu 
    # com o paddle ou não
    if Ball.pos[0] <= Paddle.pad_width + Ball.radius:
        if Ball.pos[1] <= Paddle.pos[1] or Ball.pos[1] >= Paddle.pos[1] + Paddle.pad_height:
            return False
        else:
            som1.stop()
            som1.play()
            Ball.vel[0] *= V_INCREMENT
            Ball.vel[1] *= V_INCREMENT
            Paddle.vel_inicial *= V_INCREMENT
            return True
    else:
        return None

def collision_r(Paddle, Ball):
    # Quando a bola está na linha da direita, verifica se colidiu 
    # com o paddle ou não
    if Ball.pos[0] >= WIDTH-1 - Paddle.pad_width - Ball.radius:
        if Ball.pos[1] <= Paddle.pos[1] or Ball.pos[1] >= Paddle.pos[1] + Paddle.pad_height:
            return False
        else:
            som1.stop()
            som1.play()
            Ball.vel[0] *= V_INCREMENT
            Ball.vel[1] *= V_INCREMENT
            Paddle.vel_inicial *= V_INCREMENT
            return True
    else:
        return None

def spawn_ball(Ball, Score, direction, Paddle1, Paddle2):
    global game_state
    Ball.pos[0] = WIDTH/2
    Ball.pos[1] = HEIGHT/2
    Ball.vel[0] = direction * random.randint(120, 240) / FPS
    Ball.vel[1] = random.choice([-1, 1]) * random.randint(60, 180) / FPS
    Paddle1.vel_inicial = PAD_VEL_INICIAL
    Paddle2.vel_inicial = PAD_VEL_INICIAL
    if Score.score_l == FINAL_SCORE or Score.score_r == FINAL_SCORE:
        game_state = 0


# ---------- EVENT HANDLER FUNCTION ---------- #

def event_handlers():
    global game_state
    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit(); sys.exit()

        elif event.type == pg.KEYDOWN:
            if event.key == K_ESCAPE:
                pg.quit(); sys.exit()
            else:
                paddle_l.key_event_press(event)
                paddle_r.key_event_press(event)
                if game_state == 0:
                    EndOfGame.event_handler(event)

        elif event.type == pg.KEYUP:
            paddle_l.key_event_unpress(event)
            paddle_r.key_event_unpress(event)


# ---------- DRAW HANDLER FUNCTION ---------- #

def draw_scene(surface):
    # Reta - (top left point), (bottom right point), thickness

    # Linha começa 1 pixel depois do pad, colada nele. Se fosse PAD_WIDTH-1
    # (ou WIDTH-1-PAD_WIDTH na direita) o último pixel do pad coincidiria
    # com o pixel da linha.
    pg.draw.line(surface, white, (PAD_WIDTH,0), (PAD_WIDTH, HEIGHT-1), 1)
    pg.draw.line(surface, white, (WIDTH-1-PAD_WIDTH-1, 0),
                 (WIDTH-1-PAD_WIDTH-1, HEIGHT-1), 1)

    # Círculo Central (2 círculos antialiased formando um anel)
    gfxdraw.aacircle(surface, WIDTH//2, HEIGHT//2, HEIGHT//7, white)
    gfxdraw.filled_circle(surface, WIDTH//2, HEIGHT//2, HEIGHT//7, white)
    gfxdraw.aacircle(surface, WIDTH//2, HEIGHT//2, HEIGHT//7-1, black)
    gfxdraw.filled_circle(surface, WIDTH//2, HEIGHT//2, HEIGHT//7-1, black)

    # Linha central
    pg.draw.line(surface, white, (WIDTH/2,0), (WIDTH/2, HEIGHT-1), 1)


def draw_handler(canvas):
    global game_state

    canvas.fill(black)
    draw_scene(canvas)
    score.draw(canvas)

    paddle_l.update()
    paddle_l.draw(canvas)
    paddle_r.update()
    paddle_r.draw(canvas)

    if game_state == 1:
        ball.update()
        ball.draw(canvas)
        game.update()

    elif game_state == 0:
        EndOfGame.draw(canvas)

    pg.display.update()


# ------- OTHER GLOBALS, INITIALIZATIONS, OBJECTS CREATION ------- #

paddle_l = Paddle(PAD_WIDTH, PAD_HEIGHT, 
                  [0, (HEIGHT-1)/2 - PAD_HEIGHT/2], 
                  white, pg.K_w, pg.K_s)
paddle_r = Paddle(PAD_WIDTH, PAD_HEIGHT,
                  [WIDTH-1 - PAD_WIDTH, (HEIGHT-1)/2 - PAD_HEIGHT/2],
                  white, pg.K_UP, pg.K_DOWN)
ball = Ball([WIDTH/2, HEIGHT/2], 20, red, white)
score = Score()
game = Game(score, ball, paddle_l, paddle_r)


# ------------ TIMER INITIALIZATION / MAIN LOOP ------------ #

def main():
    clock = pg.time.Clock()
    while True:
        event_handlers()
        draw_handler(canvas)
        clock.tick(FPS)


if __name__ == '__main__':
    main()
    


#!/usr/bin/env python3

# ---------- IMPORTS ---------- #

import os, sys
import pygame as pg
from pygame.locals import *
import math
import random


# ---------- GLOBAL VARIABLES ---------- #

WINDOW_TITLE = 'Asteroids'
WIDTH = 800
HEIGHT = 600
FPS = 60

time = 0  # Usado na atualização do background animado
TIMER_ID = USEREVENT + 1  # Identificação do timer (usado no spawn de asteróides)
interval = 1000  # Intervalo dos ticks do timer (em ms)
status = False  # False = Splash screen, True = Jogo em andamento

white = pg.Color(255, 255, 255)


# ---------- LOAD DE ARQUIVOS ---------- #

# Dependendo do sistema, se houver latência no áudio, pode ser necessário
# mexer em pg.mixer.init ou pg.mixer.pre_init
pg.init()

font1 = pg.font.Font('data/fonts/LiberationSerif-Regular.ttf', 25)
font2 = pg.font.Font('data/fonts/LiberationSerif-Regular.ttf', 23)

# Classe auxiliar para organizar informações das imagens carregadas

class ImageInfo:
    def __init__(self, center, size, radius=0, lifespan=None, animated=False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated


# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim

# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = pg.image.load('data/images/debris2_blue.png')
debris_scaled = pg.transform.scale(debris_image, (WIDTH, HEIGHT))

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = pg.image.load('data/images/nebula_blue.f2014.png')

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = pg.image.load('data/images/splash.png')

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = pg.image.load('data/images/double_ship.png')

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = pg.image.load('data/images/shot2.png')

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = pg.image.load('data/images/asteroid_blue.png')

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = pg.image.load('data/images/explosion_alpha.png')

# sound assets purchased from sounddogs.com, please do not redistribute
pg.mixer.music.load('data/sounds/soundtrack.wav')
missile_sound = pg.mixer.Sound('data/sounds/missile.wav')
missile_sound.set_volume(0.5)
ship_thrust_sound = pg.mixer.Sound('data/sounds/thrust.wav')
explosion_sound = pg.mixer.Sound('data/sounds/explosion.wav')

# alternative upbeat soundtrack by composer and former IIPP student Emiel Stopler
# please do not redistribute without permission from Emiel at http://www.filmcomposer.nl
#pg.mixer.music.load('data/sounds/ricerocks_theme.wav')


# ---------- INITIALIZE SCREEN ---------- #

canvas = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption(WINDOW_TITLE)

pg.mixer.music.play(-1)  # -1 = loop


# ---------- AUXILIARY FUNCTIONS ---------- #

def angle_to_vector(ang):
    return [math.cos(math.radians(ang)), math.sin(math.radians(ang))]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)

def group_collide(group, single_sprite):
    collision = 0
    for sprite in list(group):
        if sprite.collide(single_sprite):
            sprite_explosion = Sprite(sprite.pos, [0, 0], 0, 0, explosion_image,
                                      explosion_info, explosion_sound)
            explosion_group.add(sprite_explosion)
            group.remove(sprite)
            collision = 1
    return collision

def group_group_collide(group1, group2):
    collisions = 0
    for sprite in list(group2):
        if group_collide(group1, sprite):
            group2.remove(sprite)
            collisions += 1
    return collisions

# Rotaciona uma imagem (em sentido horário) em torno de seu centro.
def rotate_image(image, angle, pivot):
    rotated_image = pg.transform.rotozoom(image, -angle, 1)  # Imagem rotacionada
    rotated_rect = rotated_image.get_rect(center = pivot)  # Novo rect rotacionado, com o centro posicionado em "pivot"
    return rotated_image, rotated_rect


# ---------- CLASSES ---------- #

class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]  # Posição do centro da imagem
        self.vel = [vel[0],vel[1]]
        self.thrust = False  # Inicia com motores desligados
        self.angle = angle  # Ângulo que a ponta da nave faz com horizontal (em graus)
        self.angle_vel = 0  # Inicia sem rotação
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()

    def draw(self, surface):
        # Parâmetros: imagem, (topleft)_surface, (rect)_imag
        if self.thrust:
            thrust_ship = self.image.subsurface((ship_info.get_size()[0], 0,
                          ship_info.get_size()[0], ship_info.get_size()[1]))
            final_ship, final_ship_rect = rotate_image(thrust_ship, self.angle, 
                                                       self.pos)
            surface.blit(final_ship, final_ship_rect)
        else:
            ship = self.image.subsurface((0, 0, ship_info.get_size()[0],
                                         ship_info.get_size()[1]))
            final_ship, final_ship_rect = rotate_image(ship, self.angle, self.pos)
            surface.blit(final_ship, final_ship_rect)

    def update(self):
        self.angle += self.angle_vel

        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT

        # Existem 2 forças (2 acelerações para levar em conta): motor da nave e atrito
        # - Thrust no sentido da frente da nave: c*forward
        # - Atrito no sentido oposto ao da velocidade: -b*vel

        # vel = vel + total acceleration
        # vel = vel + c*forward - b*vel
        # vel = (1-b)*vel + c*forward
        
        b = 0.03
        self.vel[0] *= (1 - b)
        self.vel[1] *= (1 - b)

        # Vetor que aponta para a frente da nave (não-normalizado)
        forward = angle_to_vector(self.angle)
        c = 0.3
        if self.thrust:
            self.vel[0] += forward[0] * c
            self.vel[1] += forward[1] * c

    def shoot_missile(self):
        global a_missile
        forward = angle_to_vector(self.angle)
        # Míssil parte de x = center_x + (size_y)/2 * cos(alpha)
        #                 y = center_y + (size_y)/2 + sen(alpha)
        k = 4.5
        a_missile = Sprite([self.pos[0] + self.image_size[1]//2 * forward[0], self.pos[1] + self.image_size[1]//2 * forward[1]], 
                           [self.vel[0] + k*forward[0], self.vel[1] + k*forward[1]], 
                           self.angle, 0, missile_image, missile_info, missile_sound)
        missile_group.add(a_missile)

    def rotate(self, angle_vel):
        self.angle_vel = angle_vel
        
    def set_thrust(self, state):
        self.thrust = state
        if self.thrust:
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.stop()

    def key_event_press(self, event):
        if event.key == pg.K_LEFT:
            self.rotate(-5.73)
        elif event.key == pg.K_RIGHT:
            self.rotate(5.73)
        elif event.key == pg.K_UP:
            self.set_thrust(True)
        elif event.key == pg.K_SPACE:
            self.shoot_missile()

    def key_event_unpress(self, event):
        if event.key == pg.K_LEFT or event.key == pg.K_RIGHT:
            self.rotate(0)
        elif event.key == pg.K_UP:
            self.set_thrust(False)


class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound=None):
        self.pos = [pos[0],pos[1]]  # Posição do centro da imagem
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.stop()
            sound.play()

    def draw(self, surface):
        if self.animated:
            current_index = self.age
            current_topleft = [current_index * self.image_size[0], 0]
            sprite = self.image.subsurface((current_topleft, (self.image_size[0], self.image_size[1])))
            final_img, final_img_rect = rotate_image(sprite, self.angle, self.pos)
            surface.blit(final_img, final_img_rect)

        else:
            final_img, final_img_rect = rotate_image(self.image, self.angle, self.pos)
            surface.blit(final_img, final_img_rect)

    def update(self):
        self.angle += self.angle_vel
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        self.age += 1
        return self.age >= self.lifespan  # Se retorna True, sprite será removido

    def collide(self, sprite):
        center1 = self.pos
        center2 = sprite.pos
        d = dist(center1, center2)
        return d < self.radius + sprite.radius


class Score:
    def __init__(self):
        self.score = 0
        self.lives = 3

    def draw(self, surface):
        text1 = font1.render('Lives', True, white)
        surface.blit(text1, [40, 20])
        text2 = font2.render(str(self.lives), True, white)
        surface.blit(text2, [40, 50])
        text3 = font1.render('Score', True, white)
        surface.blit(text3, [WIDTH - 100, 20])
        text4 = font2.render(str(self.score), True, white)
        surface.blit(text4, [WIDTH - 100, 50])


# ---------- EVENT HANDLER FUNCTIONS ---------- #

def rock_spawner():
    a_rock_pos = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]
    a_rock = Sprite(a_rock_pos, [random.uniform(-1, 1), random.uniform(-1, 1)], 
                    0, random.uniform(-6.88, 6.88), asteroid_image, asteroid_info)
    # Impede spawn em cima da nave (permite até 12 asteróides simultâneos na tela)
    if len(rock_group) < 12 and dist(a_rock_pos, my_ship.pos) > a_rock.radius:
        rock_group.add(a_rock)

def new_game():
    global score, status
    global rock_group, missile_group, explosion_group

    score.score = 0
    score.lives = 3
    rock_group = set([])
    missile_group = set([])
    explosion_group = set([])

    pg.mixer.music.rewind()
    pg.mixer.music.play(-1)

    status = True

def event_handlers():
    global status
    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit(); sys.exit()

        elif event.type == pg.KEYDOWN:
            if event.key == K_ESCAPE:
                pg.quit(); sys.exit()
            else:
                my_ship.key_event_press(event)

        elif event.type == pg.KEYUP:
            my_ship.key_event_unpress(event)

        if status == False:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                if pg.Rect((WIDTH - splash_info.get_size()[0]) // 2,
                           (HEIGHT - splash_info.get_size()[1]) // 2, 
                            splash_info.get_size()[0],
                            splash_image.get_size()[1]).collidepoint(mouse_pos):
                    new_game()

        else:
            if event.type == TIMER_ID:
                rock_spawner()


# ---------- DRAW HANDLER FUNCTION ---------- #

def draw_scene(surface):
    global time
    time += 1
    wtime = (time/4) % WIDTH

    surface.blit(nebula_image, [0, 0], [0, 0, WIDTH, HEIGHT])
    surface.blit(debris_scaled, [wtime - WIDTH, 0], [0, 0, WIDTH, HEIGHT])
    surface.blit(debris_scaled, [wtime, 0], [0, 0, WIDTH, HEIGHT])


def draw_handler(canvas):
    global status
    draw_scene(canvas)

    my_ship.update()
    my_ship.draw(canvas)

    for missile in list(missile_group):
        if missile.update():
            missile_group.remove(missile)
    for missile in missile_group:
        missile.draw(canvas)

    if status == False:
        canvas.blit(splash_image, [(WIDTH - splash_info.get_size()[0]) // 2, 
                    (HEIGHT - splash_info.get_size()[1]) // 2])

    else:
        if group_collide(rock_group, my_ship):
            score.lives -= 1
        score.score += group_group_collide(rock_group, missile_group)

        for rock in rock_group:
            rock.draw(canvas)
        for explosion in explosion_group:
            explosion.draw(canvas)

        for rock in rock_group:
            rock.update()
        for explosion in list(explosion_group):
            if explosion.update():
                explosion_group.remove(explosion)

        if score.lives == 0:
            status = False

    score.draw(canvas)

    pg.display.update()


# ------- OTHER GLOBALS, INITIALIZATIONS, OBJECTS CREATION ------- #

my_ship = Ship([WIDTH/2, HEIGHT/2], [0, 0], 0, ship_image, ship_info)
rock_group = set([])
missile_group = set([])
explosion_group = set([])

score = Score()

pg.time.set_timer(TIMER_ID, interval)


# ------------ TIMER INITIALIZATION / MAIN LOOP ------------ #

def main():
    clock = pg.time.Clock()
    while True:
        event_handlers()
        draw_handler(canvas)
        clock.tick(FPS)


if __name__ == '__main__':
    main()
    


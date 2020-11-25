# ---------- IMPORTS ---------- #

import simplegui
import math
import random


# ---------- GLOBAL VARIABLES ---------- #

WINDOW_TITLE = 'Asteroids'
WIDTH = 800
HEIGHT = 600

score = 0
lives = 3
time = 0  # Usado na atualização do background animado


# ---------- LOAD DE ARQUIVOS ---------- #

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
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# alternative upbeat soundtrack by composer and former IIPP student Emiel Stopler
# please do not redistribute without permission from Emiel at http://www.filmcomposer.nl
#soundtrack = simplegui.load_sound("https://storage.googleapis.com/codeskulptor-assets/ricerocks_theme.mp3")


# ---------- AUXILIARY FUNCTIONS ---------- #

def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


# ---------- CLASSES ---------- #

class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]  # Posição do centro da imagem
        self.vel = [vel[0],vel[1]]
        self.thrust = False  # Inicia com motores desligados
        self.angle = angle  # Ângulo que a ponta da nave faz com horizontal (em radianos)
        self.angle_vel = 0  # Inicia sem rotação
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()

    def draw(self, canvas):
        if self.thrust:
            canvas.draw_image(self.image, [self.image_center[0] + self.image_size[0], self.image_center[1]], 
                              self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)

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

    def rotate(self, angle_vel):
        self.angle_vel = angle_vel
        
    def set_thrust(self, state):
        self.thrust = state
        if self.thrust:
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.pause()
            ship_thrust_sound.rewind()


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
            sound.rewind()
            sound.play()

    def draw(self, canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)

    def update(self):
        self.angle += self.angle_vel
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT


# ---------- EVENT HANDLER FUNCTIONS ---------- #

def keydown(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.rotate(-0.1)
    elif key == simplegui.KEY_MAP['right']:
        my_ship.rotate(0.1)
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(True)
    elif key == simplegui.KEY_MAP['space']:
        my_ship.shoot_missile()

def keyup(key):
    if key == simplegui.KEY_MAP['left'] or key == simplegui.KEY_MAP['right']:
        my_ship.rotate(0)
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(False)

def rock_spawner():
    global a_rock
    a_rock = Sprite([random.randint(0, WIDTH), random.randint(0, HEIGHT)],
                    [random.uniform(-1, 1), random.uniform(-1, 1)], 0, random.uniform(-0.12, 0.12), asteroid_image, asteroid_info)


# ---------- DRAW HANDLER FUNCTION ---------- #

def draw(canvas):
    global time
    global score, lives

    # animate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    canvas.draw_text('Lives', [40, 50], 25, 'White')
    canvas.draw_text(str(lives), [40, 80], 23, 'White')
    canvas.draw_text('Score', [WIDTH - 100, 50], 25, 'White')
    canvas.draw_text(str(score), [WIDTH - 100, 80], 23, 'White')

    a_rock.draw(canvas)
    a_missile.draw(canvas)
    my_ship.draw(canvas)

    a_rock.update()
    a_missile.update()
    my_ship.update()


# ---------- CREATE FRAME ---------- #

frame = simplegui.create_frame(WINDOW_TITLE, WIDTH, HEIGHT)
soundtrack.rewind()
soundtrack.play()


# ---------- REGISTER HANDLERS ---------- #

frame.set_draw_handler(draw)

frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)

timer = simplegui.create_timer(1000.0, rock_spawner)


# ---------- OTHER GLOBALS, OBJECTS CREATION ---------- #

my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
a_rock = Sprite([WIDTH / 3, HEIGHT / 3], [1, 1], 0, 0.06, asteroid_image, asteroid_info)
a_missile = Sprite([2 * WIDTH / 3, 2 * HEIGHT / 3], [0,0], 0, 0, missile_image, missile_info, missile_sound)


# ------------ FRAME/TIMER INITIALIZATION ------------ #

timer.start()
frame.start()



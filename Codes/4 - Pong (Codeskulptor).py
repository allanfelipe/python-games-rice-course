# ---------- IMPORTS ---------- #

import simplegui
import random


# ---------- GLOBAL VARIABLES ---------- #

WINDOW_TITLE = 'Pong'
WIDTH = 600
HEIGHT = 400

BALL_RADIUS = 20
PAD_WIDTH = 8
PAD_HEIGHT = 80
HALF_PAD_WIDTH = PAD_WIDTH / 2
HALF_PAD_HEIGHT = PAD_HEIGHT / 2
LEFT = False
RIGHT = True

paddle1_pos = HEIGHT/2 - HALF_PAD_HEIGHT  # referência no topo do paddle e não no centro
paddle2_pos = HEIGHT/2 - HALF_PAD_HEIGHT
paddle1_vel = 0
paddle2_vel = 0
V_PADDLE_INIT = 3
v_paddle = V_PADDLE_INIT

ball_pos = [0, 0]
ball_vel = [0, 0]  # em unidades de pixels/update = pixels/(1/60s)
v_increment = 1.1  # velocidade aumenta 10% a cada batida

score1 = 0
score2 = 0


# ---------- AUXILIARY FUNCTIONS ---------- #

# Desenha retângulo a partir de coordenadas = (topleft_x, topleft_y, width, height)
def rect(canvas, coord, thickness, color_in, color_out):
    canvas.draw_polygon(((coord[0], coord[1]), 
                         (coord[0] + coord[2], coord[1]), 
                         (coord[0] + coord[2], coord[1] + coord[3]), 
                         (coord[0], coord[1] + coord[3])), 
                         thickness, color_out, color_in)

# De acordo com direction, a bola é lançada para o lado superior de quem acabou
# de fazer um ponto.
def spawn_ball(direction):
    global ball_pos, ball_vel, v_paddle
    v_paddle = V_PADDLE_INIT
    ball_pos = [WIDTH/2, HEIGHT/2]
    # Range em [2,4[ px/update. Como roda em 60FPS, então range é em [120,240[ px/s
    ball_vel[0] = 2*random.random() + 2
    # Range em -[1, 3[ px/update. Como roda em 60FPS, então range é em [60,180[ px/s
    ball_vel[1] = - (2*random.random() + 1)
    if direction == LEFT:
        ball_vel[0] = -ball_vel[0]


# ---------- EVENT HANDLER FUNCTIONS ---------- #

def keydown(key):
    global paddle1_vel, paddle2_vel
    if key == simplegui.KEY_MAP['w']:
        paddle1_vel = -v_paddle
    elif key == simplegui.KEY_MAP['s']:
        paddle1_vel = v_paddle
    elif key == simplegui.KEY_MAP['up']:
        paddle2_vel = -v_paddle
    elif key == simplegui.KEY_MAP['down']:
        paddle2_vel = v_paddle

def keyup(key):
    global paddle1_vel, paddle2_vel
    if key == simplegui.KEY_MAP['w']:
        paddle1_vel = 0
    elif key == simplegui.KEY_MAP['s']:
        paddle1_vel = 0  
    elif key == simplegui.KEY_MAP['up']:
        paddle2_vel = 0  
    elif key == simplegui.KEY_MAP['down']:
        paddle2_vel = 0

def new_game():
    global paddle1_pos, paddle2_pos
    global score1, score2
    score1 = score2 = 0
    paddle1_pos = HEIGHT/2 - HALF_PAD_HEIGHT  # referência no topo do paddle e não no centro
    paddle2_pos = HEIGHT/2 - HALF_PAD_HEIGHT
    spawn_ball(random.choice([LEFT, RIGHT]))


# ---------- DRAW HANDLER FUNCTION ---------- #

def draw(canvas):
    global paddle1_pos, paddle2_pos, ball_pos, ball_vel, v_paddle, v_increment
    global score1, score2

    # draw mid line and gutters
    canvas.draw_line([WIDTH/2, 0],[WIDTH/2, HEIGHT], 1, 'White')
    canvas.draw_line([PAD_WIDTH, 0],[PAD_WIDTH, HEIGHT], 1, 'White')
    canvas.draw_line([WIDTH - PAD_WIDTH, 0],[WIDTH - PAD_WIDTH, HEIGHT], 1, 'White')

    # update ball
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # colisão cima/baixo
    if ball_pos[1] <= BALL_RADIUS:
        ball_vel[1] = -ball_vel[1]
    if ball_pos[1] >= HEIGHT - BALL_RADIUS:
        ball_vel[1] = -ball_vel[1]

    # colisão esquerda/direita + condição de pontuação
    if ball_pos[0] <= PAD_WIDTH + BALL_RADIUS:
        if ball_pos[1] > paddle1_pos and ball_pos[1] < paddle1_pos + PAD_HEIGHT:
            ball_vel[0] = -ball_vel[0]
            ball_vel[0] *= v_increment
            ball_vel[1] *= v_increment
            v_paddle *= v_increment
        else:
            score2 += 1
            spawn_ball(RIGHT)
    if ball_pos[0] >= WIDTH - PAD_WIDTH - BALL_RADIUS:
        if ball_pos[1] > paddle2_pos and ball_pos[1] < paddle2_pos + PAD_HEIGHT:
            ball_vel[0] = -ball_vel[0]
            ball_vel[0] *= v_increment
            ball_vel[1] *= v_increment
            v_paddle *= v_increment
        else:
            score1 += 1
            spawn_ball(LEFT)

    # draw scores
    canvas.draw_text(str(score1), (WIDTH/2 + 100, HEIGHT/4), 38, 'White')
    canvas.draw_text(str(score2), (WIDTH/2 - 100, HEIGHT/4), 38, 'White')

    # draw ball
    canvas.draw_circle(ball_pos, BALL_RADIUS, 2, 'White', 'Red')

    # update paddle's vertical position, keep paddle on the screen    
    if paddle1_pos + paddle1_vel >= 0 and paddle1_pos + paddle1_vel <= HEIGHT - PAD_HEIGHT:    
        paddle1_pos += paddle1_vel
    if paddle2_pos + paddle2_vel >= 0 and paddle2_pos + paddle2_vel <= HEIGHT - PAD_HEIGHT:
        paddle2_pos += paddle2_vel

    # draw paddles    
    rect(canvas,(0, paddle1_pos, PAD_WIDTH, PAD_HEIGHT), 1, 'White', 'White')
    rect(canvas,(WIDTH - PAD_WIDTH, paddle2_pos, PAD_WIDTH, PAD_HEIGHT), 1, 'White', 'White')


# ---------- CREATE FRAME ---------- #    

frame = simplegui.create_frame(WINDOW_TITLE, WIDTH, HEIGHT)


# ---------- REGISTER HANDLERS ---------- #

frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)

frame.add_button('Restart', new_game)


# ---------- OTHER GLOBALS, INITIALIZATIONS ---------- #

new_game()


# ------------ FRAME INITIALIZATION ------------ #

frame.start()

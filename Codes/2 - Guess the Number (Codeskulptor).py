# ---------- IMPORTS ---------- #

import simplegui
import random
import math


# ---------- GLOBAL VARIABLES ---------- #

WINDOW_TITLE = 'Adivinhe o número'
WIDTH = 150
HEIGHT = 150

n_max = 99
secret_number = 0
remaining = 0


# ---------- AUXILIARY FUNCTIONS ---------- #

def new_game():
    print('----- NOVO JOGO em [0, ', n_max + 1, '[ -----\n', sep='')
    global secret_number, remaining
    remaining = int(math.ceil(math.log(n_max-1) / math.log(2)))
    secret_number = random.randint(0, n_max)


def input_guess(guess):
    global remaining
    guess = int(guess)

    print('Seu palpite foi:', guess)
    remaining -= 1
    if remaining != 0:
        if guess == secret_number:
            print('Acertou!!\nIniciando um novo jogo.\n')
            new_game()
        elif guess < secret_number:
            print('Tente um número mais alto!')
            print('Palpites restantes:', remaining, '\n')
        elif guess > secret_number:
            print('Tente um número mais baixo!')
            print('Palpites restantes:', remaining, '\n')
    
    elif remaining == 0:
        if guess == secret_number:
            print('Acertou!!\nIniciando um novo jogo.\n')
            new_game()
        else:
            print('Acabaram os palpites! O número oculto era:', secret_number, '\n')
            print('Iniciando um novo jogo.\n')
            new_game()


# ---------- EVENT HANDLER FUNCTIONS ---------- #

def range100():
    global n_max
    n_max = 99
    new_game()

def range1000():
    global n_max
    n_max = 999
    new_game()


# ---------- CREATE FRAME ---------- #

frame = simplegui.create_frame(WINDOW_TITLE, WIDTH, HEIGHT)


# ---------- REGISTER HANDLERS ---------- #

frame.add_button('Jogo em [0,100[', range100)
frame.add_button('Jogo em [0,1000[', range1000)
frame.add_input('Digite o número:', input_guess, 100)


# ------------ FRAME INITIALIZATION / CALL NEW GAME ------------ #

frame.start()
new_game()


# ---------- IMPORTS ---------- #

import simplegui


# ---------- GLOBAL VARIABLES ---------- #

WINDOW_TITLE = 'What is it you want?'
WIDTH = 640
HEIGHT = 480

white = 'rgb(255,255,255)'
black = 'rgb(0, 0, 0)'
green = 'rgb(0, 255, 0)'
cyan = 'rgb(0, 255, 255)'
magenta = 'rgb(255, 0, 255)'

count = 0


# ---------- AUXILIARY FUNCTIONS/VARIABLES ---------- #

def increment():
    global count
    count += 1


# ---------- DRAW HANDLER FUNCTION ---------- #

def draw_handler(canvas):

    text1 = 'We'
    text2 = 'want...'
    text3 = 'a'
    text4 = 'shrubbery!'

    increment()
    time = count % 240  # 60 unidades = 1 segundo (update em 60FPS)

    if time < 60:
        canvas.draw_text(text1, (WIDTH//6, HEIGHT//2.1), 30, 'white')
    elif time < 120 and time >= 60:
        canvas.draw_text(text2, (WIDTH//3, HEIGHT//2.1), 30, 'green')
    elif time < 180 and time >= 120:
        canvas.draw_text(text3, (WIDTH//2, HEIGHT//2.1), 30, 'cyan')
    elif time <= 240 and time >120:
        canvas.draw_text(text4, (WIDTH//1.5, HEIGHT//2.1), 30, 'magenta')

        
# ---------- CREATE FRAME ---------- #

frame = simplegui.create_frame(WINDOW_TITLE, WIDTH, HEIGHT)


# ---------- REGISTER HANDLERS ---------- #

frame.set_draw_handler(draw_handler) 


# ------------ FRAME/TIMER INITIALIZATION ------------ #

frame.start()


# ---------- IMPORTS ---------- #

import simplegui


# ---------- GLOBAL VARIABLES ---------- #

WINDOW_TITLE = 'Stopwatch'
WIDTH = 320
HEIGHT = 240
FONT_SIZE = 60
SCORE_SIZE = 45

interval = 100   # Ticks do timer em ms (100ms = 0.1s)
count = 0
score = 0
total = 0


# ---------- AUXILIARY FUNCTIONS ---------- #

# Recebe um inteiro, que representa décimos de segundos, e retorna um 
# string no formato m:ss.d
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

def button_handler_start():
    timer.start()

def button_handler_stop():
    global score, total
    # Impede ganhar ponto ao clicar no stop quando a contagem está parada
    if timer.is_running():
        if int(format(count)[-1]) == 0:
            score += 1
        total += 1
        timer.stop()

def button_handler_reset():
    global count, score, total
    timer.stop()
    count = score = total = 0

def timer_handler():
    global count
    count += 1


# ---------- DRAW HANDLER FUNCTION ---------- #

def draw_handler(canvas):
    canvas.draw_text(format(count), 
                            [WIDTH/2 - text_width/2, 0.62*HEIGHT],
                            FONT_SIZE, 'Red')
    canvas.draw_text(str(score) + '/' + str(total),
                     [WIDTH - 1.1*score_width, 0.2*HEIGHT],
                      SCORE_SIZE, 'Green')


# ---------- CREATE FRAME ---------- #

frame = simplegui.create_frame(WINDOW_TITLE, WIDTH, HEIGHT)

text_width = frame.get_canvas_textwidth(format(0), FONT_SIZE)
score_width = frame.get_canvas_textwidth('10/10', SCORE_SIZE)

# ---------- REGISTER HANDLERS ---------- #

timer = simplegui.create_timer(interval, timer_handler)

frame.add_button('Start', button_handler_start, 100)
frame.add_button('Stop', button_handler_stop, 100)
frame.add_button('Reset', button_handler_reset, 100)

frame.set_draw_handler(draw_handler)


# ------------ FRAME INITIALIZATION ------------ #

frame.start()


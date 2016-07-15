import telebot
import urllib   
from board import Board
from telebot import types
import constant_2048
# Using the ReplyKeyboardMarkup class
# It's constructor can take the following optional arguments:
# - resize_keyboard: True/False (default False)
# - one_time_keyboard: True/False (default False)
# - selective: True/False (default False)
# - row_width: integer (default 3)
# row_width is used in combination with the add() function.
# It defines how many buttons are fit on each row before continuing on the next row.


chr_UP = u'\u2191'
chr_DOWN = u'\u2193'
chr_LEFT = u'\u2190'
chr_RIGHT = u'\u2192'
board = Board()

API_TOKEN = constant_2048.API_TOKEN

tb = telebot.TeleBot(API_TOKEN)


def getCellStr(x, y):  # TODO: refactor regarding issue #11
    """
    return a string representation of the cell located at x,y.
    """
    global board
    c = board.getCell(x, y)

    if c == 0:
        return '.'

    elif c == 1024:
        s = ' 1k'
    elif c == 2048:
        s = ' 2k'
    else:
        s = '%3d' % c

    return s



def boardToString():
    """
    return a string representation of the current board.
    """
    global board
    b = board
    rg = range(b.size())
    s = '\n'.join(
        ["┌────┬────┬────┬────┐" + 
".join([getCellStr(x, y) for x in rg]) for y in rg])"
    return s

# Handle '/start' and '/help'
@tb.message_handler(commands=['help', 'start'])
def send_welcome(message):
    global board 
    global score
    board = Board()
    score = 0
    msg = tb.reply_to(message, """\
Hi there, I am 2048bot
""")
    tb.register_next_step_handler(msg, game_start)


@tb.message_handler(commands=['game'])
def game_start(message):
    # or add strings one row at a time:
    try:
        markup = types.ReplyKeyboardMarkup()
        markup.row(chr_UP)
        markup.row(chr_LEFT, chr_DOWN, chr_RIGHT)
        tb.send_message(message.chat.id, chr_UP,reply_markup = markup)
    except e,Exception:
        send_welcome(message)

@tb.message_handler(content_types=['text'])
def game_arrow(message):
    try:
        global board
        if message.text == chr_UP:
            board.move(Board.UP)
            tb.reply_to(message, "UP")
        if message.text == chr_DOWN:
            board.move(Board.DOWN)
            tb.reply_to(message, "DOWN")
        if message.text == chr_RIGHT:
            board.move(Board.RIGHT)
            tb.reply_to(message, "RIGHT")
        if message.text == chr_LEFT:
            board.move(Board.LEFT)
            tb.reply_to(message, "LEFT")
        s = boardToString()
        tb.reply_to(message, s)
    except e,Exception:
        send_welcome(message)

tb.polling()
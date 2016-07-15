# -*- coding: utf-8 -*-
import constant_2048
import telebot
import urllib   
import logging
from board import Board
from telebot import types
import sqlite3
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
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)
def getCellStr(x, y):  # TODO: refactor regarding issue #11
    """
    return a string representation of the cell located at x,y.
    """
    global board
    c = board.getCell(x, y)

    if c == 0:
        return '    '
    elif c == 2:
        s = '  2 '
    elif c == 4:
        s = '  4 '
    elif c == 8:
        s = '  8 '
    elif c == 16:
        s = ' 16 '
    elif c == 32:
        s = ' 32 '
    elif c == 64:
        s = ' 64 '
    elif c == 128:
        s = ' 128'
    elif c == 256:
        s = ' 256'
    elif c == 512:
        s = ' 512'
    elif c == 1024:
        s = '1024'
    elif c == 2048:
        s = '2048'
    elif c == 4096:
        s = '4096'
    elif c == 8192:
        s = '8192'
    else:
        s = '%3d' % c

    return s

def boardToStringBD():
    global board
    l = []
    stringCell = ''
    array_x = range(board.size())
    print board.size()
    print array_x
    for x in array_x:
        for y in array_x:
            j = board.getCell(x,y)
            stringCell = stringCell + str(j) + ','
            l.append(j)
    return stringCell

def boardToString():
    """
    return a string representation of the current board.
    """
    global board
    b = board
    rg = range(b.size())
    s = "┌────┬────┬────┬────┐\n"+"┌────┬────┬────┬────┐\n|"+"|\n╞════╪════╪════╪════╡\n|".join(
        ['|'.join([getCellStr(x, y) for x in rg]) for y in rg])
    s = s + "|\n└────┴────┴────┴────┘"
    return s

# Handle '/start' and '/help'
@tb.message_handler(commands=['help', 'start'])
def send_welcome(message):
    msg = tb.reply_to(message, """\
Hi there, I am 2048bot. For game starting click /game
""")
    tb.register_next_step_handler(msg, game_start)

@tb.message_handler(commands=['game'])
def game_start(message):
    # or add strings one row at a time:
    global score
    markup = types.ReplyKeyboardMarkup()
    board = Board()
    score = 0
    chat_id = str(message.chat.id)
    con = sqlite3.connect('2048.db')
    with con:
        cur = con.cursor()
        cur.execute('INSERT or REPLACE INTO users (id, board) VALUES ('+chat_id+', "'+boardToStringBD()+'");')
    con.close()
    s = boardToString()
    markup.row(chr_UP)
    markup.row(chr_LEFT, chr_DOWN, chr_RIGHT)
    tb.send_message(message.chat.id, "```" + s + "```", parse_mode = "Markdown", reply_markup = markup)

@tb.message_handler(content_types=['text'])
def game_arrow(message):
    try:
        
        con = sqlite3.connect('2048.db')
        chat_id = str(message.chat.id)
        with con:
            cur = con.cursor()
            cur.execute('SELECT board FROM users WHERE id='+chat_id+';')
        data_from_db = cur.fetchone()
        
        list_from_db = []

        if data_from_db:
            list_from_db = data_from_db[0].split(',')
        else: 
            list_from_db = "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0".split(',')
        global board 
        array_x = range(board.size())
        for x in array_x:
            for y in array_x:
                print 'list from db'
                print list_from_db
                print 'array_x'
                print array_x
                j = list_from_db[4*x+y]
                if (j!=''):
                    board.setCell(x,y, int(j))
        global score
        if message.text == chr_UP:
            score += board.move(Board.UP)
        if message.text == chr_DOWN:
            score += board.move(Board.DOWN)
        if message.text == chr_RIGHT:
            score += board.move(Board.RIGHT)
        if message.text == chr_LEFT:
            score += board.move(Board.LEFT)
        
        with con:
            cur = con.cursor()
            cur.execute('INSERT or REPLACE INTO users (id, board) VALUES ('+chat_id+', "'+boardToStringBD()+'");')
        con.close()
        
        s = boardToString()
        tb.send_message(message.chat.id,  "Score: "+ str(score) + "```" + s + "```", parse_mode = "Markdown")
    except Exception:
        send_welcome(message)
tb.polling()
# -*- coding: utf-8 -*-
#import botan
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
API_TOKEN = constant_2048.API_TOKEN
botan_token = constant_2048.BOTAN_TOKEN # Token got from @botaniobot


tb = telebot.TeleBot(API_TOKEN)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)
def getCellStr(board, x, y):  # TODO: refactor regarding issue #11
    """
    return a string representation of the cell located at x,y.
    """
#    global board
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
# 2 \ud83d\ude36\n
# 4 \ud83d\ude10\n
# 8 \ud83d\ude42\n
# 16 \ud83d\ude0a\n
# 32 \ud83d\ude00\n
# 64 \ud83d\ude05\n
# 128 \ud83d\ude1d\n
# 256 \ud83d\ude02\n
# 512 \ud83d\ude07\n
# 1024 \ud83d\ude2c\n
# 2048 \ud83d\ude0e\n
# 4096 \ud83d\udc7d
    return s

def boardToStringBD(board):
#    global board
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

def boardToString(board):
    """
    return a string representation of the current board.
    """
#    global board
#    b = board
    rg = range(board.size())
    s = "┌────┬────┬────┬────┐\n"+"┌────┬────┬────┬────┐\n|"+"|\n╞════╪════╪════╪════╡\n|".join(
        ['|'.join([getCellStr(board, x, y) for x in rg]) for y in rg])
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
#    global score
    markup = types.ReplyKeyboardMarkup()
    board = Board()
    score = 0
    chat_id = str(message.chat.id)
    con = sqlite3.connect('2048.db')
    with con:
        cur = con.cursor()
        cur.execute('INSERT or REPLACE INTO users (id, board, score) VALUES ('+chat_id+', "'+boardToStringBD(board)+'", "'+str(score)+'");')
    con.close()
    s = boardToString(board)
    markup.row(chr_UP)
    markup.row(chr_LEFT, chr_DOWN, chr_RIGHT)
    tb.send_message(message.chat.id, "```" + s + "```", parse_mode = "Markdown", reply_markup = markup)
    uid = message.chat.id
    message_dict = message.to_dict()
    event_name = message.text
#    print botan.track(botan_token, uid, message_dict, event_name)



@tb.message_handler(content_types=['text'])
def game_arrow(message):
    try:
        
        con = sqlite3.connect('2048.db')
        chat_id = str(message.chat.id)
        with con:
            cur = con.cursor()
            cur.execute('SELECT board, score FROM users WHERE id='+chat_id+';')
        data_from_db = cur.fetchone()
        
        list_from_db = []

        if data_from_db:
            list_from_db = data_from_db[0].split(',')
        else: 
            list_from_db = "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0".split(',')
        if data_from_db[1]:
            score = int(data_from_db[1])
        else:
            score = 0

        board = Board()
        array_x = range(board.size())
        for x in array_x:
            print 'list from db'
            print list_from_db
            j = []
            for y in array_x:
                j.append(int(list_from_db[4*x+y]))
            print j
            if (j!=''):
                board.setCol(x, j)
        if message.text == chr_UP:
            print 'UP'
            score += board.move(Board.UP)
        if message.text == chr_DOWN:
            print 'DOWN'
            score += board.move(Board.DOWN)
        if message.text == chr_RIGHT:
            score += board.move(Board.RIGHT)
        if message.text == chr_LEFT:
            score += board.move(Board.LEFT)
        
        with con:
            cur = con.cursor()
            cur.execute('INSERT or REPLACE INTO users (id, board, score) VALUES ('+chat_id+', "'+boardToStringBD(board)+'", "'+str(score)+'");')
        con.close()
        
        s = boardToString(board)
        tb.send_message(message.chat.id,  "Score: "+ str(score) + "```" + s + "```", parse_mode = "Markdown")
    except Exception:
        print 'wtf!'
        send_welcome(message)
tb.polling()
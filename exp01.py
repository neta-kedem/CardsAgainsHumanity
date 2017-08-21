#!/usr/bin/python
import urwid
import sys, socket, select
import logging
from multiprocessing import Process

# import requests

logging.basicConfig(filename='client-logs.log', level=logging.DEBUG)
choices = 'card1 card2 card3 card4 card5 card6 card7 card8 card9 card10'.split()
general_sentence = 'bla bla ____ bla'
your_sentence = general_sentence
chosen_words = []
allowd_compleations = 1
curr_compleations = 0
curr_chosen = {}
is_czar = False
user_id = -1
NUM_OF_PLAYERS = int(sys.argv[3])
s = {}

def print_sentence_card():
    return general_sentence

def done_choosing(a):
    if(your_sentence.count('____')):
        print 'make a sentence first'
    else:
        s.send(your_sentence)
        # print(your_sentence+' DONE')
        logging.info("user id %d" % user_id)
        print("DONE!")

def sentence_chosen(a, b):
    if is_czar:
        print('YOU CHOSE', b)

def item_chosen(button, state, lable):
    global curr_compleations, allowd_compleations, general_sentence, your_sentence, main_card, curr_chosen, curr_my_cards, header, footer
    is_repeating = False
    if lable in chosen_words:
        is_repeating = True

    if((len(chosen_words) < general_sentence.count('____')) and not(is_repeating)):
        chosen_words.append(lable)
    elif(not(is_repeating)):
        chosen_words.pop(0)
        chosen_words.append(lable)

    newSentence = general_sentence
    for word in chosen_words:
        newSentence = newSentence.replace('____', word, 1)
    your_sentence = newSentence

    main_card = players_sentences([general_sentence, your_sentence])
    main = urwid.Columns([curr_my_cards, main_card])

    top = urwid.Frame(main, header, footer)
    urwid.MainLoop(top, palette).run()

    print('num of chosen items', len(curr_chosen))
    print top

def exit_program(button):
    raise urwid.ExitMainLoop()
def players_sentences(choices):
    body = [urwid.Text('Chosen Black Card:'), urwid.Text(general_sentence), urwid.Divider(),
            urwid.Text('Your sentence:'), urwid.Text(your_sentence), urwid.Divider(),
            urwid.Text('All Sentences')]
    iterchoices = iter(choices)
    next(iterchoices)
    for c in iterchoices:
        choise = print_sentence_card()
        button = urwid.Button(c)
        # button = urwid.CheckBox(c)
        # button = urwid.AttrMap(urwid.SelectableIcon([u'  * ', c], 2), None, 'selected')
        urwid.connect_signal(button, 'click', sentence_chosen, c)
        # urwid.connect_signal(button, 'change', item_chosen, c)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))
    return urwid.ListBox(urwid.SimpleListWalker(body))
def my_cards(choices):
    body = [urwid.Text('My Cards'), urwid.Divider()]
    for c in choices:
        button = urwid.CheckBox(c)
        urwid.connect_signal(button, 'change', item_chosen, c)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))
    done_btn = urwid.Button('done')
    urwid.connect_signal(done_btn, 'click', done_choosing)
    body.append(urwid.AttrMap(done_btn, None, focus_map='reversed'))
    return urwid.ListBox(urwid.SimpleListWalker(body))

def chat_client():
    global user_id, s, select
    # logging.debug("s = %s " % s)
    # while 1:
    logging.debug("AM I EVEN HERE")

    socket_list = [sys.stdin, s]

    # Get the list sockets which are readable
    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
    for sock in read_sockets:
        if sock == s:
            # incoming message from remote server, s
            data = sock.recv(4096)
            logging.info("a data %s" % data)
            if not data:
                logging.info("Disconnected from chat server")
                # print '\nDisconnected from chat server'
                sys.exit()
            else:
                logging.info("user if sock is s and data: %s" % data)
                # sys.stdout.write(data)
                # sys.stdout.write('[Me] ');
                # sys.stdout.flush()


        else:
            # user entered a message
            msg = sys.stdin.readline()
            logging.info("user if sock is not s and msg: %s" % msg)
            s.send(msg)

def urwid_main_loop():
    logging.debug("AM I EVEN THERE")
    global top, palette
    urwid.MainLoop(top, palette).run()


header = urwid.AttrWrap(urwid.Text(["Cards Against Humanity"]), 'reversed')
str = ''
if not is_czar:
    str = ' Not'
footer = urwid.AttrWrap(urwid.Text(["You Are%s The Czar" % str]), 'reversed')
footer = urwid.AttrWrap(urwid.Text(["%d" %user_id]), 'reversed')
main_card = players_sentences([general_sentence])
curr_my_cards = my_cards(choices)
main = urwid.Columns([curr_my_cards, main_card])
top = urwid.Frame(main, header, footer)

'''
top = urwid.Overlay(main, urwid.SolidFill(u'\N{MEDIUM SHADE}'),
    align='left', width=('relative', 60),
    valign='top', height=('relative', 100),
    min_width=20, min_height=9)
'''
palette =[
        ('reversed', 'standout', ''),
        ('col', 'standout', ''),
        ('regular', '', '')
        ]
# r = requests.get('http://localhost:3000/')
# print(r.status_code, r.reason)
# print(r.text)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)

if (len(sys.argv) < 3):
    print 'Usage : python exp01.py hostname port players_num'
    sys.exit()

host = sys.argv[1]
port = int(sys.argv[2])

# connect to remote host
try:
    s.connect((host, port))
except:
    sys.exit()


# socket_list = [sys.stdin, s]

# chat_client()
# P1 = Process(target=urwid_main_loop)
P2 = Process(target=chat_client)
P2.start()
urwid_main_loop()
# P1.start()



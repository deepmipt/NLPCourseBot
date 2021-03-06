# -*- coding: utf-8 -*-
import os

token = os.environ['TOKEN']

hw_possible_to_pass = ['hw1','hw2']
hw_possible_to_check = []
quizzes_possible_to_check = ['quiz 1','quiz 2']
admins = ['fogside', 'madrugado']
current_quiz_name = 'quiz 3'
quiz_path = './quizzes/quiz3.json'
quizzes_need_to_check = 1
quiz_closed = False
pics_path = './quizzes/pics'
dump_graph_path = './backup/graph.dump'
dump_quiz_path = './backup/quiz.dump'
load_graph = False
load_states = False

marks = [str(i) for i in range(1, 6)]
available_hw_resolutions = ('zip', 'rar', '7z', 'tar', 'tar.bz2', 'tar.gz', 'tar.xz', 'ipynb')
bd_name = '/home/fogside/Projects/NLPCourseBot/questions.db'

WEBHOOKS_AVAIL = False
WEBHOOK_HOST = '<webhook addr here>'
PORT = 8444
WEBHOOK_LISTEN = '127.0.0.1'

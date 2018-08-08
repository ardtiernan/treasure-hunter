from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
import json
import random


# Create your views here.

"""
1. If request.method != POST, I want to render the page with the first question.
That means I'll need to grab a question from the database.



if request.method == 'POST'
"""

class PartyTime(object):

    user_id = None
    game_over = False
    submitted_question = None
    submitted_answer = None
    question_count = None
    truth_count = None
    truth_percentage = None
    questions_list = ["What did you do today?",
        "What are you doing after this?",
        "Have you found any treasure recently?",
        "What's your latest find?",
        "Why do you keep looking at your watch?",
        "Do you want to come back to mine for a drink?",
        "Is your latest find valuable?"]
    # questions_list = ["What did you do today?","What are you doing after this?","Have you found any treasure recently?","What's your latest find?","Why do you keep looking at your watch?","Do you want to come back to mine for a drink?","Is your latest find valuable?"]
    random_question = None
    answers_list = []

    def instantiate_session(self):
        # Hacky way of getting a unique id
        # SQL generates the serial number when you insert the random value
        # And then you grab that serial number back using the random value
        id_grabber = random.uniform(0,1)
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO id_generator(random_number)\
                            VALUES (%s);", (id_grabber,))
            cursor.execute("SELECT id FROM id_generator\
                            WHERE random_number = %s\
                            ORDER BY id DESC\
                            LIMIT 1;", (str(id_grabber),))
            self.user_id = cursor.fetchone()[0]

    def party_first_hour(self):
        with connection.cursor() as cursor:
            for i in range(33):
                cursor.execute("INSERT INTO question_answer(user_id,question,answer)\
                                VALUES (%s, 'past question', 'truth')", (self.user_id,))
            for i in range(7):
                cursor.execute("INSERT INTO question_answer(user_id,question,answer)\
                                VALUES (%s, 'past question', 'lie')", (self.user_id,))

    def grab_random_question(self):
        self.random_question = random.choice(self.questions_list)
        print('random_question1: ', self.random_question)

    def get_previous_answers(self):
        print('user_id: ', self.user_id)
        print('random_question: ', self.random_question)
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT(answer) FROM question_answer\
                            WHERE user_id = %s\
                            AND question = %s;", (self.user_id,self.random_question))
            listA = cursor.fetchall()
            print('answers_list: ', listA)
            print('ANSWERSLIST: ', self.answers_list)
            self.answers_list = []
            for answer in listA:
                self.answers_list.append(answer[0])

    def get_post_values(self,request):
        self.user_id = request.POST.get('user_id','unassigned')
        self.submitted_question = request.POST.get('question','unassigned')
        self.submitted_answer = request.POST.get('answer','unassigned').lower()
        print('user_id: ', self.user_id)
        print('submitted_question: ', self.submitted_question)
        print('submit_answer: ', self.submitted_answer)

    def submit_answer(self):
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO question_answer(user_id,question,answer)\
                            VALUES (%s, %s, %s);", (self.user_id,self.submitted_question,self.submitted_answer))

    def calc_question_count(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT SUM(question_count) FROM(\
                                SELECT COUNT(question) question_count FROM question_answer\
                                WHERE user_id = %s\
                                GROUP BY question\
                                HAVING COUNT(question) > 1) AAA", (self.user_id,))
            question_count = cursor.fetchone()[0]
            print('question_count: ', question_count)
            qualified_count = self.qualifying_questions()
            question_count = question_count - qualified_count + 1
        return question_count

    def qualifying_questions(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(question) FROM (\
                                SELECT question FROM question_answer\
                                WHERE user_id = %s\
                                GROUP BY question\
                                HAVING COUNT(question) > 1\
                            ) AAA;", (self.user_id,))
            qualified_count = cursor.fetchone()[0]
            print('qualified_count: ', qualified_count)
        return int(qualified_count)

    def calc_truth_count(self):
        with connection.cursor() as cursor:
            cursor.execute("WITH BBB AS (\
                                SELECT question, COUNT(answer) answer_count\
                                FROM question_answer\
                                WHERE user_id = %s\
                                AND question IN (\
	                               SELECT question FROM question_answer\
                                   WHERE user_id = %s\
	                               GROUP BY question\
                                   HAVING COUNT(question) > 1\
                                )\
                                GROUP BY question, answer\
                            ),\
                            CCC AS (\
                                SELECT question, MAX(answer_count) max_count\
                                FROM BBB\
                                GROUP BY question\
                            )\
                            SELECT SUM(max_count) FROM CCC", (self.user_id,self.user_id))
            truth_count = cursor.fetchone()[0]
            print('truth_count: ', truth_count)
        return truth_count

    def calc_truth_percentage(self):
        question_count = self.calc_question_count()
        truth_count = self.calc_truth_count()
        self.truth_percentage = truth_count / question_count

    def calc_game_status(self):
        if self.truth_percentage >= 0.8 and self.truth_percentage <= 0.9:
            self.game_over = False
        else:
            self.game_over = True

    def compile_initial_dictionary(self):
        context_dict = {'user_id': self.user_id,
                        'question': self.random_question}
        return context_dict

    def compile_dictionary(self):
        print('random_question2: ', self.random_question)
        context_dictA = {'question': self.random_question,
                        'answers_list': self.answers_list,
                        'game_over': self.game_over,
                        'truth_percentage': str(self.truth_percentage)}
        context_dict = {'context': json.dumps(context_dictA)}
        return context_dict


def initial_page_load(request):

    party = PartyTime()
    party.instantiate_session()
    party.party_first_hour()
    party.grab_random_question()
    context_dict = party.compile_initial_dictionary()

    return render(request,'treasurehunter.html',context=context_dict)


def dinnerpartyAJAX(request):

    party = PartyTime()

    if request.is_ajax():
        party.get_post_values(request)
        party.submit_answer()
        party.calc_truth_percentage()
        party.calc_game_status()

        if party.game_over == False:
            party.grab_random_question()
            party.get_previous_answers()

        context_dict = party.compile_dictionary()
        return HttpResponse(json.dumps(context_dict), content_type='application/json')

    else:
        data = "Not AJAX"
        return HttpResponse(data, content_type='application/json')

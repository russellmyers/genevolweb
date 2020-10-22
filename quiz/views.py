from django.shortcuts import render
from django.conf import settings
import json

import logging
logger = logging.getLogger(__name__)

# Create your views here.

def load_quiz(quiz_code):
    file_name = settings.BASE_DIR + '/static/quiz/' + quiz_code + '.json'
    with open(file_name) as json_file:
        j  = json.load(json_file)

    return j


def quiz(request):
    quiz_code_requested = request.GET.get('quiz-code', 'GENEV')
    max_questions = request.GET.get('questions', -1)

    logger.info(f'Quiz - code: {quiz_code_requested} max_questions: {max_questions}')

    terms = load_quiz(quiz_code_requested)
    context= {"terms": terms, 'max_questions': max_questions}

    return render(request, "quiz/quiz.html", context=context)

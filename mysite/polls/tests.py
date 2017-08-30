import datetime
from django.test import TestCase
from django.utils import timezone
from .models import Question
from django.urls import reverse


def create_question(question_text, days):
    '''
     Create a question with given 'question_text' and publish the given number of 'days'
     offset to now (negative for questions published in the past, positive for questions
     that have yet to be published).
    '''
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        '''
        was_published_recently() returns False for questions whose pub_date is in the future.
        '''
        time = timezone.localtime(timezone.now()) + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        '''
        was_published_recently() returns False for questions whose pub_date is in the past.
        '''
        time = timezone.localtime(timezone.now()) - datetime.timedelta(days=1)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        '''
        was_published_recently() returns True for questions whose pub_date is within the last day.
        '''
        time = timezone.localtime(timezone.now()) - datetime.timedelta(hours=23, minutes=59, seconds=59)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        '''
        If no questions exists, an appropriate message is displayed.
        '''
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        '''
        Questions with a pub_date in the past are displayed on the index page.
        '''
        create_question(question_text='Past Question.', days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past Question.>']
                                 )

    def test_future_question(self):
        '''
        Questions with a pub_date in the future are not displayed on the index.
        '''
        create_question(question_text='Future Question.', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            []
        )


    def test_future_and_past_question(self):
        '''
        Even if both future and past questions exist, only past questions are displayed.
        '''
        create_question(question_text='Past Question', days=-30)
        create_question(question_text='Future Question', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past Question>']
        )


    def test_two_past_questions(self):
        '''
        The questions index page may display multiple questions.
        '''
        create_question(question_text='Past Question1', days=-30)
        create_question(question_text='Past Question2', days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past Question2>', '<Question: Past Question1>']
        )

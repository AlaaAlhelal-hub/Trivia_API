import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', '1234','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # set data for testing
        self.new_question = {'question':'Who is the inventor of the light bulb?',
        'answer' : 'Thomas Edison',
        'difficulty' : 1,
        'category' : 1}

        self.new_question2 = {'id':1,
        'question':'What is the capital of Saudi Arabia',
        'answer' : 'Riyadh',
        'difficulty' : 1,
        'category' : 3}

        self.invalid_question = {'question':'What is the capital of Saudi Arabia',
        'answer' : 'Riyadh'}

        self.search_term = {'searchTerm':'capital'}

        self.play_quiz = {
            'previous_questions': [],
            'quiz_category': {'type': 'Science', 'id': 1}
        }
        self.invalid_play_quiz = {
            'previous_questions': [],
            'quiz_category': None
        }
        self.non_existent_question = {'id':1000,
        'question':' ',
        'answer' : ' ',
        'difficulty' : 1,
        'category' : 3}


        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    ''' Test get_categories '''
    def test_get_categories(self):
        res = self.client().get('/categories')
        #load te data from response
        data=json.loads(res.data)
        #make sure the status code is ok (200)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    ''' Test get_questions '''
    def test_get_questions(self):
        res = self.client().get('/questions')
        #load te data from response
        data=json.loads(res.data)
        #make sure the status code is ok (200)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    ''' Test get_questions invalid page number'''
    def test_404_sent_request_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        #load te data from response
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resourse not found')

    ''' Test post new question '''
    def test_add_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data=json.loads(res.data)
        #make sure the status code is created (201)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['current_questions']))
        self.assertTrue(data['total_questions'])

    ''' Test post new question invalid data'''
    def test_400_add_invalid_question(self):
        res = self.client().post('/questions', json=self.invalid_question)
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')

    ''' Test Delete question '''
    def test_delete_question(self):
        init_res = self.client().post('/questions', json=self.new_question2)
        question_to_delete = json.loads(init_res.data)['created']

        res = self.client().delete(f'/questions/{question_to_delete}')
        data = json.loads(res.data)
        deleted_question = Question.query.filter(Question.id==question_to_delete).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_to_delete)
        self.assertTrue(len(data['current_questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(deleted_question, None)

    ''' Test if question colud not be deleted  '''
    def test_405_unallowed_method(self):
        res = self.client().post('/questions/404')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    ''' Test if question does not exist  '''
    def test_422_delete_non_existent_question(self):
        res = self.client().delete('/questions/404', json=self.non_existent_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    ''' Test get questions based on a search term'''
    def test_search_for_questions(self):
        res = self.client().post('/questions/search', json=self.search_term)
        data=json.loads(res.data)
        #make sure the status code is ok (200)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    ''' Test search if term is empty '''
    def test_422_search_for_questions(self):
        res = self.client().post('/questions/search', json={'searchTerm':None})
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    ''' Test get_questions_based_on_category'''
    def test_get_questions_based_on_category(self):
        res = self.client().get('/categories/6/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['current_category'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    ''' Test get questions based on invalid category'''
    def test_404_get_questions_from_invalid_category(self):
        res = self.client().get('/categories/8/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resourse not found')

    ''' Test play quiz'''
    def test_play(self):
        res = self.client().post('/quizzes', json=self.play_quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    ''' Test play quiz invalid '''
    def test_422_play_invalid_quiz(self):
        res = self.client().post('/quizzes', json=self.invalid_play_quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')






# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

import os
import unittest2
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest2.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question={
            'question': 'What is the capitol of the UK?',
            'answer': 'London',
            'category': 2,
            'difficulty': 1
        }

        self.search={
            'searchTerm': 'largest lake'
        }

        self.next_quiz_question={
            'previous_questions': [1],
            'quiz_category': { 'id': 2}
        }        

        #binds the app to the current context
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

    def test_get_categories_success(self):
        """Test get Categories"""
        res = self.client().get('/categories')
        print(res)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['categories']), 6)

    def test_get_questions_success (self):
        """Test get Categories"""
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(len(data['categories']), 6)
        self.assertEqual(data['currentCategory'], None)

    def test_get_questions_404_sent_request_beyond_valid_page(self):
        res = self.client().get('/questions?page=100')
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')
    
    def test_delete_question_success(self):
        res=self.client().delete('/questions/10')
        data=json.loads(res.data)

        question=Question.query.filter(Question.id==10).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 10)
        self.assertEqual(question, None)
    
    def test_delete_question_422_error(self):
        res=self.client().delete('/questions/432')
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    def test_create_question_success(self):
        res=self.client().post('/questions', json=self.new_question)
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_search_question(self):
        res=self.client().post('/questions/search', json=self.search)
        data=json.loads(res.data)

        self.assertEqual(data['total_questions'], 1)

    def test_questions_by_category_success(self):
        res=self.client().get('/categories/1/questions')
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['currentCategory'], 1)
        self.assertEqual(len(data['questions'])>0, True)
    
    def test_404_no_questions_by_category_found(self):
        res=self.client().get('/categories/31/questions')
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    def test_play_quiz_success(self):
        res=self.client().post('/quizzes', json=self.next_quiz_question)
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question'] is not None, True)
     
    
    def test_404_questions_for_quiz_not_found(self):
        invalid_category={
            'previous_questions': [1],
            'quiz_category': { 'id': 25}
        } 

        res=self.client().post('/quizzes', json=invalid_category)
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest2.main()
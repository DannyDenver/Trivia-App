import os
from flask import Flask, request, abort, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys
from models import db
import random
from sqlalchemy import func

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  ''' 
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response
    
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def categories():
    categories=Category.query.all()
    formatted_categories=[cat.format() for cat in categories]
    categoryDict = {}

    for cat in formatted_categories:
      categoryDict[cat['id']] = cat['type']

    return jsonify({
      'categories': categoryDict
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions', methods=['GET'])
  def questions():
    page = request.args.get('page', default=1, type=int)
    start = (page-1) * 10
    end = start + 10
    questions=Question.query.all()
    categories= Category.query.all()
    
    categoryDict = {}
    formatted_questions=[question.format() for question in questions]

    current_questions=formatted_questions[start:end]

    if len(current_questions) == 0:
      abort(404)

    formatted_categories=[cat.format() for cat in categories]
    for cat in formatted_categories:
      categoryDict[cat['id']] = cat['type']
      
    return jsonify({
      'questions': current_questions,
      'total_questions': len(questions),
      'categories': categoryDict,
      'currentCategory': None
    })



  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    try:
      db.session.query(Question).get(id).delete()
      db.session.commit()
    except: 
      db.session.rollback()
      abort(404)
    finally:
      db.session.close()
    
    return jsonify({
      'success':True,
      'deleted': id
    })

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    questionForm=request.get_json()
    try: 
      question=Question(question=questionForm['question'],
        answer=questionForm['answer'],
        category=questionForm['category'],
        difficulty=questionForm['difficulty'])

      db.session.add(question)
      db.session.commit()
    except:
      db.session.rollback()
      print(sys.exc_info())
      abort(422)
    finally:
      db.session.close()

    return jsonify({ 'success': True})

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    search=request.get_json()
    questions=Question.query.filter(func.lower(Question.question).contains(func.lower(search['searchTerm']))).all()

    return jsonify({
      'questions': [question.format() for question in questions],
      'total_questions': len(questions)     
    })


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only q
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def questions_by_category(category_id):
    page = request.args.get('page', default=1, type=int)
    start = (page-1) * 10
    end = start + 10
    questions=Question.query.filter_by(category=category_id).all()
    print(questions)
    if len(questions)==0:
      abort(404)

    categories= Category.query.all()
    
    categoryDict = {}
    formatted_questions=[question.format() for question in questions]
    formatted_categories=[cat.format() for cat in categories]

    for cat in formatted_categories:
      categoryDict[cat['id']] = cat['type']
      
    return jsonify({
      'questions': formatted_questions[start:end],
      'totalQuestions': len(formatted_questions),
      'categories': categoryDict,
      'currentCategory': category_id
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    quizSettings=request.get_json()
    categoryId=quizSettings['quiz_category']['id']

    questions=Question.query.filter_by(category=categoryId).all()

    if len(questions)==0:
      abort(404)

    formattedQuestions=[question.format() for question in questions]

    previousQuestions = quizSettings['previous_questions']

    questionsLeft=list(filter(lambda x: x['id'] not in previousQuestions, formattedQuestions))
    return jsonify({
      'question': random.choice(questionsLeft) if len(questionsLeft) > 0 else None
    })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request_error(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad Request'
    }), 400

  @app.errorhandler(404)
  def not_found_error(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Not Found'
    }), 404

  @app.errorhandler(422)
  def unprocessable_entity_error(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable Entity'
    }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal Server Error'
    }), 500
    
  
  return app

    
import os
from xml.dom import ValidationErr
from flask import Flask
from models import *
from flask_cors import CORS, cross_origin
from flask import Flask, request, abort, jsonify, make_response
from datetime import date, datetime
PER_PAGE = 10

def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.route('/')
    def welcome_app(): 
        return jsonify({'App': 'General Specifications Application'})

    @app.route('/create-categories', methods = ['POST'])
    def create_categories():
        try:
            validate_require = []
            if request.json['title'] == "":
                validate_require.append("Please enter a title!")

            if len(validate_require) > 0:
                return jsonify({"validate": validate_require})
            
            category = Categories(
                title=request.json['title']
            )
            Categories.insert(category)
            return jsonify({
                "response": f"Created [{category.title}] successfully"
            })
        except ValidationErr as err:
            return jsonify({
                "messages": err.messages,
                "validate": validate_require
            }), 400

    @app.route('/get-categories')
    def get_categories():
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', PER_PAGE, type=int)
            
            total = Categories.query.count()
            categories = Categories.query.paginate(page=page, per_page=per_page)
            formatted_categories = [cate.format() for cate in categories.items]
            return jsonify({
                "success": True,
                "categories": formatted_categories,
                "total": total
            })
        except IndexError as e:
            print(e)
            abort(404)
    
    @app.route('/delete-categories/<int:category_id>', methods=["DELETE"])
    @cross_origin() 
    def delete_question(category_id):
        try:
            category = Categories.query.get_or_404(category_id)
            Categories.delete(category)
            return jsonify({"result": f"Delete {category_id} successfully"})
        except IndexError as e:
            print(e)
            abort(404)
    
    @app.route('/update-categories', methods=['PATCH'])
    def update_categories():
        try:
            validate_require = []
            if request.json['title'] == "":
                validate_require.append("Please enter a title")
                
            if request.json['id'] == 0:
                validate_require.append("Please enter a id")

            if len(validate_require) > 0:
                return jsonify({"validate": validate_require})
            
            category = Categories.query.get_or_404(request.json['id'])
            category.title=request.json['title']
            Categories.update(category)
            return jsonify({
                "response": f"Updated [{category.title}] successfully"
            })
        except ValidationErr as err:
            return jsonify({
                "messages": err.messages,
                "validate": validate_require
            }), 400
    
    
    
    
    
    
    
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run()

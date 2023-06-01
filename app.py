import os
import itertools
from xml.dom import ValidationErr
from flask import Flask
from sqlalchemy import asc, func
from models import *
from flask_cors import CORS, cross_origin
from flask import Flask, request, abort, jsonify, make_response
from datetime import date, datetime
from flask import Flask, request, jsonify, abort
import json
import ssl
from .auth.auth import AuthError, requires_auth
PER_PAGE = 10

def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    ssl._create_default_https_context = ssl._create_stdlib_context

    @app.route('/')
    def welcome_app(): 
        return jsonify({'App': 'General Specifications Application'})

    @app.route('/create-category', methods = ['POST'])
    def create_category():
        try:
            validate_require = []
            if request.json['title'] == "":
                validate_require.append("Please enter a title!")

            if len(validate_require) > 0:
                return jsonify({"validate": validate_require})
            
            id = 0
            categoryDb = Categories.query.order_by(Categories.id.desc()).first()
            if (categoryDb != None):
                id = categoryDb.id
                
            category = Categories(
                id = id + 1,
                title = request.json['title']
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
    @requires_auth('get:drinks-detail')
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
    
    @app.route('/delete-category/<int:category_id>', methods=["DELETE"])
    @cross_origin() 
    def delete_category(category_id):
        try:
            category = Categories.query.get_or_404(category_id)
            Categories.delete(category)
            return jsonify({"result": f"Deleted {category_id} successfully"})
        except IndexError as e:
            print(e)
            abort(404)
    
    @app.route('/update-category', methods=['PATCH'])
    def update_category():
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
    
    
    @app.route('/create-product', methods = ['POST'])
    def create_product():
        try:
            validate_require = []
            if request.json['category_id'] == None or request.json['category_id'] == 0:
                validate_require.append("Please enter a category_id!")
                
            if request.json['name'] == "":
                validate_require.append("Please enter a name!")
                
            if request.json['price'] == None or request.json['price'] == 0:
                validate_require.append("Please enter a price!")
                
            if request.json['quantity'] == None or request.json['quantity'] == 0:
                validate_require.append("Please enter a quantity!")

            if len(validate_require) > 0:
                return jsonify({"validate": validate_require})
            
            id = 0
            productDb = Products.query.order_by(Products.id.desc()).first()
            if (productDb != None):
                id = productDb.id
                
            product = Products(
                id = id + 1,
                category_id = request.json['category_id'],
                name = request.json['name'],
                price = request.json['price'],
                quantity = request.json['quantity']
            )
            Products.insert(product)
            return jsonify({
                "response": f"Created [{product.name}] successfully"
            })
        except ValidationErr as err:
            return jsonify({
                "messages": err.messages,
                "validate": validate_require
            }), 400
    
    
    @app.route('/get-products')
    def get_products():
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', PER_PAGE, type=int)
            
            total = Products.query.count()
            products = Products.query.paginate(page=page, per_page=per_page)
            formatted_products = [pro.format() for pro in products.items]
            return jsonify({
                "success": True,
                "categories": formatted_products,
                "total": total
            })
        except IndexError as e:
            print(e)
            abort(404)
    
    @app.route('/delete-product/<int:product_id>', methods=["DELETE"])
    @cross_origin() 
    def delete_product(product_id):
        try:
            product = Products.query.get_or_404(product_id)
            Products.delete(product)
            return jsonify({"result": f"Deleted {product_id} successfully"})
        except IndexError as e:
            print(e)
            abort(404)
    
    @app.route('/update-product', methods=['PATCH'])
    def update_product():
        try:
            validate_require = []
            if request.json['category_id'] == None or request.json['category_id'] == 0:
                validate_require.append("Please enter a category_id!")
                
            if request.json['name'] == "":
                validate_require.append("Please enter a name!")
                
            if request.json['price'] == None or request.json['price'] == 0:
                validate_require.append("Please enter a price!")
                
            if request.json['quantity'] == None or request.json['quantity'] == 0:
                validate_require.append("Please enter a quantity!")

            if len(validate_require) > 0:
                return jsonify({"validate": validate_require})
            
            product = Products.query.get_or_404(request.json['id'])
            product.category_id = request.json['category_id']
            product.name = request.json['name']
            product.price = request.json['price']
            product.quantity = request.json['quantity']
            Categories.update(product)
            
            return jsonify({
                "response": f"Updated [{product.name}] successfully"
            })
        except ValidationErr as err:
            return jsonify({
                "messages": err.messages,
                "validate": validate_require
            }), 400
    
    
    # Error Handling
    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        response = jsonify({
            "error": ex.error,
            "status_code": ex.status_code,
            "message": ex.message
        })
        response.status_code = ex.status_code
        return response


    @app.errorhandler(404)
    def resource_not_found_error_handler(error):
        return jsonify({
            'success': False,
            'message': 'Auth error'
        }), 401


    @app.errorhandler(404)
    def resource_not_found_error_handler(error):
        return jsonify({
            'success': False,
            'message': 'resource not found'
        }), 404


    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run()

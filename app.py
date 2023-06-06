from flask import (
  Flask,
  request,
  abort,
  jsonify
)
from database.models import (
    ActorInMovie,
    setup_db,
    Actor,
    Movie
)
import sys
from auth.auth import AuthError, requires_auth
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import Blueprint
agency_blueprint = Blueprint('agency_blueprint', __name__)

def create_app():
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"/*": {"origins": "*"}})
    #ssl._create_default_https_context = ssl._create_stdlib_context

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @agency_blueprint.route('/')
    def home():
        return "Casting Agency Specifications", 200

    @agency_blueprint.route('/actors')
    @requires_auth("get:actors")
    def get_actors(payload):
        actors_query = Actor.query.order_by(Actor.id).all()
        actors = [actor.short_info for actor in actors_query]

        return jsonify({
            "success": True,
            "actors": actors
        }), 200

    @agency_blueprint.route('/actors/<int:actor_id>')
    @requires_auth("get:actors-info")
    def get_actor_by_id(payload, actor_id):
        actor = Actor.query.get_or_404(actor_id)

        return jsonify({
            "success": True,
            "actor": actor.full_info
        }), 200

    @agency_blueprint.route('/actors', methods=['POST'])
    @requires_auth("post:actor")
    def create_actor(payload):
        try:
            request_body = request.get_json()
            if 'name' not in request_body \
                    or 'date_of_birth' not in request_body:
                raise KeyError

            if request_body['name'] == '' \
                    or request_body['date_of_birth'] == '':
                raise ValueError

            full_name = ''
            if 'full_name' in request_body:
                full_name = request_body["full_name"]

            new_actor = Actor(request_body['name'], full_name,
                              request_body['date_of_birth'])
            new_actor.save()

            return jsonify({
                "success": True,
                "created_actor_id": new_actor.id
            }), 201

        except (TypeError, KeyError, ValueError):
            abort(422)

        except Exception:
            print(sys.exc_info())
            abort(500)

    @agency_blueprint.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth("patch:actor")
    def update_actor(payload, actor_id):
        actor = Actor.query.get_or_404(actor_id)

        try:
            request_body = request.get_json()
            if not bool(request_body):
                raise TypeError

            if "name" in request_body:
                if request_body["name"] == "":
                    raise ValueError

                actor.name = request_body["name"]

            if "full_name" in request_body:
                if request_body["full_name"] == "":
                    raise ValueError

                actor.full_name = request_body["full_name"]

            if 'date_of_birth' in request_body:
                if request_body["date_of_birth"] == "":
                    raise ValueError

                actor.date_of_birth = request_body["date_of_birth"]

            actor.update()

            return jsonify({
                "success": True,
                "actor_info": actor.long_info
            }), 200

        except (TypeError, ValueError, KeyError):
            abort(422)

        except Exception:
            print(sys.exc_info())
            abort(500)

    @agency_blueprint.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth("delete:actor")
    def delete_actor(payload, actor_id):
        actor = Actor.query.get_or_404(actor_id)

        try:
            actor.delete()

            return jsonify({
                "success": True,
                "deleted_actor_id": actor.id
            }), 200

        except Exception:
            print(sys.exc_info())
            abort(500)

    @agency_blueprint.route('/movies')
    @requires_auth("get:movies")
    def get_movies(payload):
        movies_query = Movie.query.order_by(Movie.id).all()
        movies = [movie.short_info for movie in movies_query]

        return jsonify({
            "success": True,
            "movies": movies
        }), 200

    @agency_blueprint.route('/movies/<int:movie_id>')
    @requires_auth("get:movies-info")
    def get_movie_by_id(payload, movie_id):
        movie = Movie.query.get_or_404(movie_id)

        return jsonify({
            "success": True,
            "movie": movie.full_info
        }), 200

    @agency_blueprint.route('/movies', methods=['POST'])
    @requires_auth("post:movie")
    def create_movie(payload):
        try:
            request_body = request.get_json()

            if 'title' not in request_body \
                    or 'release_year' not in request_body \
                    or 'duration' not in request_body \
                    or 'imdb_rating' not in request_body \
                    or 'cast' not in request_body:
                raise KeyError

            if request_body['title'] == '' \
                    or request_body['release_year'] <= 0 \
                    or request_body['duration'] <= 0 \
                    or request_body['imdb_rating'] < 0 \
                    or request_body["imdb_rating"] > 10 \
                    or len(request_body["cast"]) == 0:
                raise TypeError

            new_movie = Movie(
                request_body['title'],
                request_body['release_year'],
                request_body['duration'],
                request_body['imdb_rating']
            )
            actors = Actor.query.filter(
                Actor.name.in_(request_body["cast"])).all()

            if len(request_body["cast"]) == len(actors):
                new_movie.save()
                for actor in actors:
                    actor_in_movie = ActorInMovie(new_movie.id, actor.id)
                    actor_in_movie.save()
            else:
                raise ValueError

            return jsonify({
                "success": True,
                "created_movie_id": new_movie.id
            }), 201

        except (TypeError, KeyError, ValueError) as e:
            abort(422)

        except Exception as ess:
            print(sys.exc_info())
            abort(500)

    @agency_blueprint.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth("patch:movie")
    def update_movie(payload, movie_id):
        movie = Movie.query.get_or_404(movie_id)

        try:
            request_body = request.get_json()
            if not bool(request_body):
                raise TypeError

            if "title" in request_body:
                if request_body["title"] == "":
                    raise ValueError

                movie.title = request_body["title"]

            if "release_year" in request_body:
                if request_body["release_year"] <= 0:
                    raise ValueError

                movie.release_year = request_body["release_year"]

            if "duration" in request_body:
                if request_body["duration"] <= 0:
                    raise ValueError

                movie.duration = request_body["duration"]

            if "imdb_rating" in request_body:
                if request_body["imdb_rating"] < 0 \
                        or request_body["imdb_rating"] > 10:
                    raise ValueError

                movie.imdb_rating = request_body["imdb_rating"]

            if "cast" in request_body:
                if len(request_body["cast"]) == 0:
                    raise ValueError

                actors = Actor.query.filter(
                    Actor.name.in_(request_body["cast"])).all()

                if len(request_body["cast"]) == len(actors):
                    movie.cast = actors
                else:
                    raise ValueError

            movie.update()

            return jsonify({
                "success": True,
                "movie_info": movie.long_info
            }), 200

        except (TypeError, ValueError, KeyError):
            abort(422)

        except Exception:
            print(sys.exc_info())
            abort(500)

    @agency_blueprint.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth("delete:movie")
    def delete_movie(payload, movie_id):
        movie = Movie.query.get_or_404(movie_id)

        try:
            movie.delete()

            return jsonify({
                "success": True,
                "deleted_movie_id": movie.id
            }), 200

        except Exception:
            print(sys.exc_info())
            abort(500)

    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        """
        Receive the raised authorization error and propagates it as response
        """
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response

    @app.errorhandler(400)
    @app.errorhandler(401)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(405)
    @app.errorhandler(422)
    @app.errorhandler(500)
    def error_handler(error):
        return jsonify({
            'success': False,
            'error': error.code,
            'message': error.description
        }), error.code

    return app


app = create_app()
app.register_blueprint(agency_blueprint)
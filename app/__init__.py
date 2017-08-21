from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
# local import
from instance.config import app_config
from flask import request, jsonify, abort, make_response

# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    """
    Method used to create an app and initialize it with the required configurations
    :param config_name:
    :return: app
    """
    from app.models import Bucketlist, User, BucketlistItem

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_object(app_config[config_name])
    db.init_app(app)

    @app.route('/bucketlists/', methods=['POST', 'GET'])
    @app.route('/bucketlists', methods=['POST', 'GET']) # for query parameter for pagination
    def bucketlists():
        """
        Method to add a bucketlist or retrieve all bucketlists
        :return: response
        """
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authenticated

                if request.method == "POST":
                    name = str(request.data.get('name', ''))
                    if name:
                        bucketlist = Bucketlist(name=name, created_by=user_id)
                        bucketlist.save()
                        response = jsonify({
                            'id': bucketlist.id,
                            'name': bucketlist.name,
                            'date_created': bucketlist.date_created,
                            'date_modified': bucketlist.date_modified,
                            'created_by': user_id
                        })

                        return make_response(response), 201

                else:
                    # get the query string for limit if it exists and for pagination
                    # if the query parameter for limit doesn't exist, 20 is used by default
                    limit = request.args.get('limit', 'default 20')
                    try:
                        limit = int(limit)
                    except ValueError:
                        # if limit value is gibberish, default to 20
                        limit = 20

                    # if limit supplied is greater than 100, display only 100
                    if limit > 100:
                        limit = 100

                    # set the default page to display to 1
                    page = 1

                    # GET all the bucketlists created by this user
                    bucketlists = Bucketlist.query.filter_by(created_by=user_id).paginate(page, limit)
                    results = []

                    for bucketlist in bucketlists.items:
                        obj = {
                            'id': bucketlist.id,
                            'name': bucketlist.name,
                            'date_created': bucketlist.date_created,
                            'date_modified': bucketlist.date_modified,
                            'created_by': bucketlist.created_by
                        }
                        results.append(obj)

                    return make_response(jsonify(results)), 200
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

    @app.route('/bucketlists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def bucketlist_manipulation(id):
        """
        Method to retrieve a bucketlist of a given id and then manipulate it accordingly
        :param id:
        :return: response
        """
        # get the access token from the authorization header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Get the user id related to this access token
            user_id = User.decode_token(access_token)

            if not isinstance(user_id, str):
                # If the id is not a string(error), we have a user id
                # Get the bucketlist with the id specified from the URL (<int:id>)
                bucketlist = Bucketlist.query.filter_by(id=id).first()
                if not bucketlist:
                    # There is no bucketlist with this ID for this User, so
                    # Raise an HTTPException with a 404 not found status code
                    abort(404)

                if request.method == "DELETE":
                    # delete the bucketlist using our delete method
                    bucketlist.delete()
                    return {
                               "message": "bucketlist {} deleted".format(bucketlist.id)
                           }, 200

                elif request.method == 'PUT':
                    # Obtain the new name of the bucketlist from the request data
                    name = str(request.data.get('name', ''))

                    bucketlist.name = name
                    bucketlist.save()

                    response = {
                        'id': bucketlist.id,
                        'name': bucketlist.name,
                        'date_created': bucketlist.date_created,
                        'date_modified': bucketlist.date_modified,
                        'created_by': bucketlist.created_by
                    }
                    return make_response(jsonify(response)), 200
                else:
                    # Handle GET request, sending back the bucketlist to the user
                    response = {
                        'id': bucketlist.id,
                        'name': bucketlist.name,
                        'date_created': bucketlist.date_created,
                        'date_modified': bucketlist.date_modified,
                        'created_by': bucketlist.created_by
                    }
                    return make_response(jsonify(response)), 200
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                # return an error response, telling the user he is unauthorized
                return make_response(jsonify(response)), 401

    @app.route('/bucketlists/<int:id>/items/', methods=['POST'])
    def bucketlist_items(id):
        """
        Method that executes creation of a new bucketlist item and adding it to the given bucketlist with <id>:id
        :param id:
        :return:
        """
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authenticated

                # Get the bucketlist with the id specified from the URL (<int:id>)
                bucketlist = Bucketlist.query.filter_by(id=id).first()
                if not bucketlist:
                    # There is no bucketlist with this ID for this User, so
                    # Raise an HTTPException with a 404 not found status code
                    abort(404)

                if request.method == "POST":
                    name = str(request.data.get('name', ''))
                    if name:
                        # Get the bucketlist items from the bucketlist with the id specified from the URL (<int:id>)
                        bucketlist_item = BucketlistItem(name=name, belongs_to=id)
                        bucketlist_item.save()
                        response = jsonify({
                            'id': bucketlist_item.id,
                            'name': bucketlist_item.name,
                            'date_created': bucketlist_item.date_created,
                            'date_modified': bucketlist_item.date_modified,
                            'done': bucketlist_item.done
                        })

                        return make_response(response), 201
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

    @app.route('/bucketlists/<int:id>/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
    def bucketlist_items_manipulation(id, item_id):
        """
        Method to retrieve an item with <id>:item_id from a bucketlist with <id>:id and manipulate it according to the request passed
        :param id:
        :param item_id:
        :return:
        """
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authenticated

                # Get the bucketlist with the id specified from the URL (<int:id>)
                bucketlist = Bucketlist.query.filter_by(id=id).first()
                if not bucketlist:
                    # There is no bucketlist with this ID for this User, so
                    # Raise an HTTPException with a 404 not found status code
                    abort(404)

                # Get the bucketlist item with the id specified from the URL (<int:item_id>)
                bucketlist_item = BucketlistItem.query.filter_by(id=item_id).first()
                if not bucketlist_item:
                    # There is no bucketlist item with this ID for this User, so
                    # Raise an HTTPException with a 404 not found status code
                    abort(404)

                if request.method == "DELETE":
                    # delete the bucketlist using our delete method
                    bucketlist_item.delete()
                    return {
                               "message": "bucketlist item {} deleted".format(bucketlist_item.id)
                           }, 200

                elif request.method == 'PUT':
                    # Obtain the new name of the bucketlist item from the request data
                    name = str(request.data.get('name', ''))

                    bucketlist_item.name = name
                    bucketlist_item.save()

                    response = {
                        'id': bucketlist_item.id,
                        'name': bucketlist_item.name,
                        'date_created': bucketlist_item.date_created,
                        'date_modified': bucketlist_item.date_modified,
                        'done': bucketlist_item.done
                    }
                    return make_response(jsonify(response)), 200
                else:
                    # Handle GET request, sending back the bucketlist to the user
                    response = {
                        'id': bucketlist_item.id,
                        'name': bucketlist_item.name,
                        'date_created': bucketlist_item.date_created,
                        'date_modified': bucketlist_item.date_modified,
                        'done': bucketlist_item.done
                    }
                    return make_response(jsonify(response)), 200
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                # return an error response, telling the user he is Unauthorized
                return make_response(jsonify(response)), 401

    # import the authentication blueprint and register it on the app
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app

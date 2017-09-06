from . import bucketlists_blueprint
from sqlalchemy import and_
from flask import request, jsonify, abort, make_response, url_for
from app.models import Bucketlist, User, BucketlistItem
from instance.config import Config


# for query parameter for pagination and searching
@bucketlists_blueprint.route('/bucketlists', methods=['POST', 'GET'])
def bucketlists():
    """
    Method to add a bucketlist or retrieve all bucketlists
    :return: response
    """

    # check if the header with key is present
    if 'Authorization' not in request.headers:
        # Return a message to the user telling them that they need to submit an authorization header with token
        response = {
            'message': 'Header with key Authorization missing.'
        }
        return make_response(jsonify(response)), 401
    else:
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')

        # check for when authorization was not provided in header
        if not auth_header:
            # Return a message to the user telling them that they need to submit an authorization header with token
            response = {
                'message': 'Token not provided in the header with key Authorization.'
            }
            return make_response(jsonify(response)), 401
        else:

            auth_strings = auth_header.split(" ")
            if len(auth_strings) != 2:
                response = {
                    'message': 'Invalid token format.'
                }
                return make_response(jsonify(response)), 401
            else:
                access_token = auth_header.split(" ")[1]

                if access_token:
                    # Attempt to decode the token and get the User ID
                    user_id = User.decode_token(access_token)
                    if not isinstance(user_id, str):
                        # Go ahead and handle the request, the user is authenticated
                        if request.method == "POST":
                            if 'name' not in request.data:
                                # Return a message to the user telling them that they need to submit a name
                                response = {
                                    'message': 'Parameter name missing.'
                                }
                                return make_response(jsonify(response)), 400
                            else:
                                name = str(request.data.get('name', ''))
                                if name:
                                    # query whether a bucketlist with the same name already exists
                                    bucketlists = Bucketlist.query.filter_by(
                                        created_by=user_id, name=name).first()
                                    if bucketlists:
                                        # Return a message to the user telling them that they need to submit a name
                                        response = {
                                            'message': 'Bucketlist with this name already exists. '
                                                       'Edit it or choose another name.'
                                        }
                                        return make_response(jsonify(response)), 409
                                    else:
                                        bucketlist = Bucketlist(
                                            name=name, created_by=user_id)
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
                                    # Return a message to the user telling them that they need to submit a name
                                    response = {
                                        'message': 'Bucketlist name should not be empty.'
                                    }
                                    return make_response(jsonify(response)), 400

                        else:
                            # get the query string for limit if it exists and for pagination
                            # if the query parameter for limit doesn't exist, 20 is used by default
                            limit = request.args.get('limit', 'default ' + str(Config.DEFAULT_PAGINATION_LIMIT))
                            try:
                                limit = int(limit)
                            except ValueError:
                                # if limit value is gibberish, default to 20
                                limit = Config.DEFAULT_PAGINATION_LIMIT

                            # if limit supplied is greater than 100, display only 100
                            if limit > Config.MAXIMUM_PAGINATION_LIMIT:
                                limit = Config.MAXIMUM_PAGINATION_LIMIT

                            # set the default page to display to 1
                            page = request.args.get('page', 'default 1')

                            try:
                                page = int(page)
                            except ValueError:
                                # if page value is gibberish, default to 1
                                page = 1

                            if limit < 1 or page < 1:
                                return abort(404, 'Page or Limit must be greater than 1')

                            # get the query string for q - this is searching based on name
                            search_string = request.args.get('q')

                            # check if a search parameter was provided
                            if search_string:
                                # get bucketlists whose name contains the search string
                                bucketlists = Bucketlist.query.filter_by(created_by=user_id).filter(
                                    Bucketlist.name.like('%' + search_string + '%')).paginate(page, limit)
                            else:
                                # GET all the bucketlists created by this user
                                bucketlists = Bucketlist.query.filter_by(
                                    created_by=user_id).paginate(page, limit)

                            results = []

                            if page == 1:
                                prev_page = url_for('.bucketlists') + '?limit={}'.format(limit)
                            else:
                                prev_page = url_for('.bucketlists') + '?limit={}&page={}'.format(limit, page - 1)

                            if page < bucketlists.pages:
                                next_page = url_for('.bucketlists') + '?limit={}&page={}'.format(limit, page + 1)
                            else:
                                next_page = None

                            for bucketlist in bucketlists.items:
                                obj = {
                                    'id': bucketlist.id,
                                    'name': bucketlist.name,
                                    'date_created': bucketlist.date_created,
                                    'date_modified': bucketlist.date_modified,
                                    'items': [{'id': item.id,
                                               'name': item.name,
                                               'date_created': item.date_created,
                                               'date_modified': item.date_modified,
                                               'done': item.done
                                               }
                                              for item in bucketlist.bucketlist_items
                                              ],
                                    'created_by': bucketlist.created_by
                                }
                                results.append(obj)

                            return make_response(jsonify({'page': page,
                                                          'items_per_page': limit,
                                                          'total_items': bucketlists.total,
                                                          'total_pages': bucketlists.pages,
                                                          'prev_page': prev_page,
                                                          'next_page': next_page,
                                                          'items': results})), 200
                    else:
                        # user is not legit, so the payload is an error message
                        message = user_id
                        response = {
                            'message': message
                        }
                        return make_response(jsonify(response)), 401
                else:
                    response = {
                        'message': 'Empty token string'
                    }
                    return make_response(jsonify(response)), 401


@bucketlists_blueprint.route('/bucketlists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def bucketlist_manipulation(id):
    """
    Method to retrieve a bucketlist of a given id and then manipulate it accordingly
    :param id:
    :return: response
    """
    # check if the header with key is present
    if 'Authorization' not in request.headers:
        # Return a message to the user telling them that they need to submit an authorization header with token
        response = {
            'message': 'Header with key Authorization missing.'
        }
        return make_response(jsonify(response)), 401
    else:
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')

        # check for when authorization was not provided in header
        if not auth_header:
            # Return a message to the user telling them that they need to submit an authorization header with token
            response = {
                'message': 'Token not provided in the header with key Authorization.'
            }
            return make_response(jsonify(response)), 401
        else:

            auth_strings = auth_header.split(" ")
            if len(auth_strings) != 2:
                response = {
                    'message': 'Invalid token format.'
                }
                return make_response(jsonify(response)), 401
            else:
                access_token = auth_header.split(" ")[1]

                if access_token:
                        # Get the user id related to this access token
                    user_id = User.decode_token(access_token)

                    if not isinstance(user_id, str):
                            # If the id is not a string(error), we have a user id
                            # Get the bucketlist with the id specified from the URL (<int:id>)
                        bucketlist = Bucketlist.query.filter_by(
                            id=id, created_by=user_id).first()
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
                            if 'name' not in request.data:
                                    # Return a message to the user telling them that they need to submit a name
                                response = {
                                    'message': 'Parameter name missing.'
                                }
                                return make_response(jsonify(response)), 400
                            else:
                                name = str(request.data.get('name', ''))
                                if name:
                                        # query whether a bucketlist with the same name already exists
                                    bucketlists = Bucketlist.query.filter(and_(
                                        Bucketlist.created_by == user_id, Bucketlist.name == name, Bucketlist.id != id)).first()
                                    if bucketlists:
                                        # Return a message to the user telling them that they need to submit a name
                                        response = {
                                            'message': 'Bucketlist with this name already exists. Choose another name.'
                                        }
                                        return make_response(jsonify(response)), 409
                                    else:
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
                                    # Return a message to the user telling them that they need to submit a name
                                    response = {
                                        'message': 'Bucketlist name should not be empty.'
                                    }
                                    return make_response(jsonify(response)), 400

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
                else:
                    response = {
                        'message': 'Empty token string'
                    }
                    return make_response(jsonify(response)), 401


@bucketlists_blueprint.route('/bucketlists/<int:id>/items/', methods=['POST', 'GET'])
def bucketlist_items(id):
    """
    Method that executes creation of a new bucketlist item and adding it to the given bucketlist with <id>:id
    :param id:
    :return:
    """
    # check if the header with key is present
    if 'Authorization' not in request.headers:
        # Return a message to the user telling them that they need to submit an authorization header with token
        response = {
            'message': 'Header with key Authorization missing.'
        }
        return make_response(jsonify(response)), 401
    else:
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')

        # check for when authorization was not provided in header
        if not auth_header:
            # Return a message to the user telling them that they need to submit an authorization header with token
            response = {
                'message': 'Token not provided in the header with key Authorization.'
            }
            return make_response(jsonify(response)), 401
        else:

            auth_strings = auth_header.split(" ")
            if len(auth_strings) != 2:
                response = {
                    'message': 'Invalid token format.'
                }
                return make_response(jsonify(response)), 401
            else:
                access_token = auth_header.split(" ")[1]

                if access_token:
                    # Attempt to decode the token and get the User ID
                    user_id = User.decode_token(access_token)
                    if not isinstance(user_id, str):
                        # Go ahead and handle the request, the user is authenticated

                        # Get the bucketlist with the id specified from the URL (<int:id>) for the logged in user
                        bucketlist = Bucketlist.query.filter_by(
                            id=id, created_by=user_id).first()
                        if not bucketlist:
                            # There is no bucketlist with this ID for this User, so
                            # Raise an HTTPException with a 404 not found status code
                            abort(404)

                        # adding a new item to the bucketlist
                        if request.method == "POST":
                            if 'name' not in request.data:
                                # Return a message to the user telling them that they need to submit a name
                                response = {
                                    'message': 'Parameter name missing.'
                                }
                                return make_response(jsonify(response)), 400
                            else:
                                name = str(request.data.get('name', ''))
                                if name:
                                    # query whether a bucketlist item with the same name already
                                    # exists in this bucketlist
                                    bucketlist_items = BucketlistItem.query.filter(and_(
                                        BucketlistItem.belongs_to == id, BucketlistItem.name == name)).first()
                                    if bucketlist_items:
                                        # Return a message to the user telling them that the bucketlist exists
                                        response = {
                                            'message': 'Bucketlist item with this name already exists in this'
                                                       ' bucketlist. Choose another name.'
                                        }
                                        return make_response(jsonify(response)), 409
                                    else:
                                        # Save the bucketlist item with the given name in the bucketlist with the id
                                        # specified from the URL (<int:id>)
                                        bucketlist_item = BucketlistItem(
                                            name=name, belongs_to=id)
                                        bucketlist_item.save()
                                        response = jsonify({
                                            'id': bucketlist_item.id,
                                            'name': bucketlist_item.name,
                                            'date_created': bucketlist_item.date_created,
                                            'date_modified': bucketlist_item.date_modified,
                                            'done': bucketlist_item.done,
                                            'belongs_to': bucketlist_item.belongs_to
                                        })

                                        return make_response(response), 201
                                else:
                                    # Return a message to the user telling them that they need to submit a name
                                    response = {
                                        'message': 'Bucketlist item name should not be empty.'
                                    }
                                    return make_response(jsonify(response)), 400
                        else:
                            # GET all the bucketlist items created by this user and belonging to this bucketlist
                            bucketlist_items = BucketlistItem.query.filter_by(
                                belongs_to=id)

                            results = []

                            for bucketlist_item in bucketlist_items.items:
                                obj = {
                                    'id': bucketlist_item.id,
                                    'name': bucketlist_item.name,
                                    'date_created': bucketlist_item.date_created,
                                    'date_modified': bucketlist_item.date_modified,
                                    'done': bucketlist_item.done,
                                    'belongs_to': bucketlist_item.belongs_to
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
                else:
                    response = {
                        'message': 'Empty token string'
                    }
                    return make_response(jsonify(response)), 401


@bucketlists_blueprint.route('/bucketlists/<int:id>/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
def bucketlist_items_manipulation(id, item_id):
    """
    Method to retrieve an item with <id>:item_id from a bucketlist with <id>:id and manipulate it according to the request passed
    :param id:
    :param item_id:
    :return:
    """
    # check if the header with key is present
    if 'Authorization' not in request.headers:
        # Return a message to the user telling them that they need to submit an authorization header with token
        response = {
            'message': 'Header with key Authorization missing.'
        }
        return make_response(jsonify(response)), 401
    else:
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')

        # check for when authorization was not provided in header
        if not auth_header:
            # Return a message to the user telling them that they need to submit an authorization header with token
            response = {
                'message': 'Token not provided in the header with key Authorization.'
            }
            return make_response(jsonify(response)), 401
        else:

            auth_strings = auth_header.split(" ")
            if len(auth_strings) != 2:
                response = {
                    'message': 'Invalid token format.'
                }
                return make_response(jsonify(response)), 401
            else:
                access_token = auth_header.split(" ")[1]

                if access_token:
                    # Attempt to decode the token and get the User ID
                    user_id = User.decode_token(access_token)
                    if not isinstance(user_id, str):
                        # Go ahead and handle the request, the user is authenticated

                        # Get the bucketlist with the id specified from the URL (<int:id>)
                        bucketlist = Bucketlist.query.filter_by(
                            id=id, created_by=user_id).first()
                        if not bucketlist:
                            # There is no bucketlist with this ID for this User, so
                            # Raise an HTTPException with a 404 not found status code
                            abort(404)

                        # Get the bucketlist item with the id specified from the URL (<int:item_id>)
                        bucketlist_item = BucketlistItem.query.filter_by(
                            id=item_id, belongs_to=id).first()
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
                            if 'name' not in request.data:
                                # Return a message to the user telling them that they need to submit a name
                                response = {
                                    'message': 'Parameter name missing.'
                                }
                                return make_response(jsonify(response)), 400
                            else:
                                # Obtain the new name of the bucketlist item from the request data
                                name = str(request.data.get('name', ''))
                                if name:
                                    # query whether a bucketlist item with the same name already exists in
                                    # the bucketlist
                                    bucketlist_items = BucketlistItem.query.filter(
                                        and_(BucketlistItem.belongs_to == id, BucketlistItem.name == name,
                                             BucketlistItem.id != item_id)).first()
                                    if bucketlist_items:
                                        # Return a message to the user telling them that they need to submit a name
                                        response = {
                                            'message': 'Bucketlist item with this name already exists in this '
                                                       'bucketlist. Choose another name.'
                                        }
                                        return make_response(jsonify(response)), 409
                                    else:
                                        bucketlist_item.name = name
                                        bucketlist_item.save()

                                        response = {
                                            'id': bucketlist_item.id,
                                            'name': bucketlist_item.name,
                                            'date_created': bucketlist_item.date_created,
                                            'date_modified': bucketlist_item.date_modified,
                                            'done': bucketlist_item.done,
                                            'belongs_to': bucketlist_item.belongs_to
                                        }
                                        return make_response(jsonify(response)), 200
                                else:
                                    # Return a message to the user telling them that they need to submit a name
                                    response = {
                                        'message': 'Bucketlist item name should not be empty.'
                                    }
                                    return make_response(jsonify(response)), 400
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
                else:
                    response = {
                        'message': 'Empty token string'
                    }
                    return make_response(jsonify(response)), 401

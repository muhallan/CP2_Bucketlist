import re
from . import auth_blueprint

from flask.views import MethodView
from flask import make_response, request, jsonify
from app.models import User


class RegistrationView(MethodView):
    """This class registers a new user."""

    def post(self):
        """ Register a new user
        ---
        tags:
          - "auth"
        parameters:
          - in: "body"
            name: "body"
            description: "Email and password submitted"
            required: true
            schema:
              type: "object"
              required:
              - "email"
              - "password"
              properties:
                email:
                  type: "string"
                password:
                  type: "string"
        responses:
            409:
              description: " Username is already taken"
            201:
              description: " Success"
            401:
              description: " Invalid Payload"
        """

        if 'email' not in request.data and 'password' not in request.data:
            # Return a message to the user telling them that they need to submit the email and password
            response = {
                'message': 'Email address and password not provided.'
            }
            return make_response(jsonify(response)), 400

        elif 'email' not in request.data:
            # Return a message to the user telling them that they need to submit the email
            response = {
                'message': 'Email address not provided.'
            }
            return make_response(jsonify(response)), 400

        elif 'password' not in request.data:
            # Return a message to the user telling them that they need to submit the password
            response = {
                'message': 'Password not provided.'
            }
            return make_response(jsonify(response)), 400
        else:
            email = request.data['email']
            password = request.data['password']

            # check if an email and a password were both not empty
            if not email and not password:
                # Return a message to the user telling them that they need to submit the email and password
                response = {
                    'message': 'Email address and password is empty.'
                }
                return make_response(jsonify(response)), 400

            # check if an email was empty
            elif not email:
                # Return a message to the user telling them that they need to submit the email
                response = {
                    'message': 'Email address is empty.'
                }
                return make_response(jsonify(response)), 400

            # check if a password was empty
            elif not password:
                # Return a message to the user telling them that they need to submit the password
                response = {
                    'message': 'Password is empty.'
                }
                return make_response(jsonify(response)), 400

            # both parameters provided
            else:
                if (not re.match("^[^@]+@[^@]+\.[^@]+$", email)) and (len(password) < 5):
                    # Return a message to the user telling them that they need to submit a correct email and password
                    response = {
                        'message': 'Invalid email address and short password.'
                    }
                    return make_response(jsonify(response)), 400

                elif not re.match("^[^@]+@[^@]+\.[^@]+$", email):
                    # Return a message to the user telling them that they need to submit a correct email
                    response = {
                        'message': 'Invalid email address.'
                    }
                    return make_response(jsonify(response)), 400

                elif len(password) < 5:
                    # Return a message to the user telling them that they need to submit a correct password
                    response = {
                        'message': 'Password too short.'
                    }
                    return make_response(jsonify(response)), 400

                else:
                    # check to see if the user already exists
                    user = User.query.filter_by(email=request.data['email']).first()

                    if not user:
                        # There is no user so we'll try to register them
                        try:
                            post_data = request.data
                            # Register the user
                            email = post_data['email']
                            password = post_data['password']
                            user = User(email=email, password=password)
                            user.save()

                            response = {
                                'message': 'You registered successfully. Please log in.'
                            }
                            # return a response notifying the user that they registered successfully
                            return make_response(jsonify(response)), 201
                        except Exception as e:
                            # An error occured, therefore return a string message containing the error
                            response = {
                                'message': str(e)
                            }
                            return make_response(jsonify(response)), 401
                    else:
                        # There is an existing user.
                        # Return a message to the user telling them that they already exist
                        response = {
                            'message': 'User already exists. Please login.'
                        }

                        return make_response(jsonify(response)), 409


class LoginView(MethodView):
    """This class-based view handles user login and access token generation."""

    def post(self):
        """ Login in a registered user
            ---
            tags:
              - "auth"
            parameters:
              - in: "body"
                name: "body"
                description: "Email and password submitted"
                required: true
                schema:
                  type: "object"
                  required:
                  - "email"
                  - "password"
                  properties:
                    email:
                      type: "string"
                    password:
                      type: "string"
            responses:
                401:
                  description: " Invalid credentials"
                201:
                  description: " Success"
                400:
                  description: " Invalid Payload"
            """

        if 'email' not in request.data and 'password' not in request.data:
            # Return a message to the user telling them that they need to submit the email and password
            response = {
                'message': 'Email address and password not provided.'
            }
            return make_response(jsonify(response)), 400

        elif 'email' not in request.data:
            # Return a message to the user telling them that they need to submit the email
            response = {
                'message': 'Email address not provided.'
            }
            return make_response(jsonify(response)), 400

        elif 'password' not in request.data:
            # Return a message to the user telling them that they need to submit the password
            response = {
                'message': 'Password not provided.'
            }
            return make_response(jsonify(response)), 400
        else:
            email = request.data['email']
            password = request.data['password']

            # check if an email and a password were both not empty
            if not email and not password:
                print("here")
                # Return a message to the user telling them that they need to submit the email and password
                response = {
                    'message': 'Email address and password is empty.'
                }
                return make_response(jsonify(response)), 400

            # check if an email was empty
            elif not email:
                # Return a message to the user telling them that they need to submit the email
                response = {
                    'message': 'Email address is empty.'
                }
                return make_response(jsonify(response)), 400

            # check if a password was empty
            elif not password:
                # Return a message to the user telling them that they need to submit the password
                response = {
                    'message': 'Password is empty.'
                }
                return make_response(jsonify(response)), 400

            else:
                try:
                    # Get the user object using their email because it is unique
                    user = User.query.filter_by(email=request.data['email']).first()

                    # Try to authenticate the found user using their password
                    if user and user.password_is_valid(request.data['password']):
                        # Generate the access token. This will be used as the authorization header
                        access_token = user.generate_token(user.id)
                        if access_token:
                            response = {
                                'message': 'You logged in successfully.',
                                'access_token': access_token.decode()
                            }
                            return make_response(jsonify(response)), 200
                    else:
                        # User does not exist. Therefore, we return an error message
                        response = {
                            'message': 'Invalid email or password, Please try again'
                        }
                        return make_response(jsonify(response)), 401

                except Exception as e:
                    # Create a response containing an string error message
                    response = {
                        'message': str(e)
                    }
                    # Return a server error using the HTTP Error Code 500 (Internal Server Error)
                    return make_response(jsonify(response)), 500


registration_view = RegistrationView.as_view('register_view')
login_view = LoginView.as_view('login_view')

# Define the rule for the registration url  /auth/register
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=registration_view,
    methods=['POST'])

# Define the rule for the registration url  /auth/login
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/auth/login',
    view_func=login_view,
    methods=['POST'])

from app import db
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta


class User(db.Model):
    """
    This is the users table where users who sign up with our app are stored
    """

    __tablename__ = 'users'

    # Define the columns of the users table, starting with the primary key
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    bucketlists = db.relationship(
        'Bucketlist', order_by='Bucketlist.id', cascade="all, delete-orphan")

    def __init__(self, email, password):
        """Initialize the user with an email and a password."""
        self.email = email
        self.password = Bcrypt().generate_password_hash(password).decode()

    def password_is_valid(self, password):
        """
        Checks the password against it's hash to validates the user's password
        """
        return Bcrypt().check_password_hash(self.password, password)

    def save(self):
        """Save a user to the database.
        This includes creating a new user and editing one.
        """
        db.session.add(self)
        db.session.commit()

    def generate_token(self, user_id):
        """ Generates the access token"""

        from run import app

        try:
            # set up a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=5),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            # create the byte string token using the payload and the SECRET key
            jwt_string = jwt.encode(
                payload,
                app.config['SECRET'],
                algorithm='HS256'
            )
            return jwt_string

        except Exception as e:
            # return an error in string format if an exception occurs
            print(str(e))
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decodes the access token from the Authorization header."""

        from run import app

        try:
            # decode the token using the SECRET variable
            payload = jwt.decode(token, app.config['SECRET'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # the token is invalid, return an error string
            return "Invalid token. Please register or login"


class Bucketlist(db.Model):
    """
    This is the bucketlist table where all bucketlists are saved.
    """

    __tablename__ = 'bucketlists'

    # columns of the table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey(User.id))

    def __init__(self, name, created_by):
        """
        Init method to initialize a bucketlist with its name and the one who created it
        :param name:
        """
        self.name = name
        self.created_by = created_by

    def save(self):
        """
        To save a new or edit a bucketlist to the database
        :return:
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all(user_id):
        """
        To get all the bucketlists for a specified user
        :param self:
        :return:
        """
        return Bucketlist.query.filter_by(created_by=user_id)

    def delete(self):
        """
        To delete an existing bucketlist from the database
        :return:
        """
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        """
        Represents the object instance of the model
        :return: the bucketlist description
        """
        return "<Bucketlist: {}>".format(self.name)

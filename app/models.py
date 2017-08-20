from app import db
from flask_bcrypt import Bcrypt


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
        

class Bucketlist(db.Model):
    """This is the bucketlist table where all bucketlists are saved."""

    __tablename__ = 'bucketlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self, name):
        """
        Init method to initialize a bucketlist
        :param name:
        """
        self.name = name

    def save(self):
        """
        To save a new or edit a bucketlist to the database
        :return:
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all(self):
        """
        To get all the bucketlists that are saved
        :param self:
        :return:
        """
        return Bucketlist.query.all()

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

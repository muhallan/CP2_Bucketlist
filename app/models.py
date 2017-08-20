from app import db


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
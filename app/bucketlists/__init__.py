from flask import Blueprint

# This instance of a Blueprint that represents the bucketlists blueprint
# added v1 to indicate that this is version 1
bucketlists_blueprint = Blueprint('buckets', __name__, url_prefix='/api/v1')

from . import bucketlists

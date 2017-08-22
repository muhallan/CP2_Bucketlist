from flask import Blueprint

# This instance of a Blueprint that represents the authentication blueprint
# added v1 to indicate that this is version 1
auth_blueprint = Blueprint('auth', __name__, url_prefix='/api/v1')

from . import views

from flask import Blueprint

# This instance of a Blueprint that represents the authentication blueprint
auth_blueprint = Blueprint('auth', __name__, url_prefix='/api/v1') # added v1 to indicate that this is version 1

from . import views

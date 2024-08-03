from flask import Blueprint

# Creating blueprint for homer higher/lower game
homer_bp = Blueprint('homer', __name__)

# Import routes after blueprints are created
from . import homer_routes

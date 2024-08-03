from flask import Blueprint

# Creating blueprint for winner higher/lower game
winner_bp = Blueprint('winner', __name__)

# Import routes after blueprints are created
from . import winner_routes

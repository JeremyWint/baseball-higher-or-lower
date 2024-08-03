from flask import Blueprint

# Creating blueprint for hitter higher/lower game
hitter_bp = Blueprint('hitter', __name__)

# Import routes after blueprints are created
from . import hitter_routes

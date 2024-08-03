from flask import Blueprint

# Creating blueprint for batter higher/lower game
batter_bp = Blueprint('batter', __name__)

# Import routes after blueprints are created
from . import batter_routes

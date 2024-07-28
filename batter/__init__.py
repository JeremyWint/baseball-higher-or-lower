from flask import Blueprint

# Creating blueprint for batter higher/lower game
batter_bp = Blueprint('batter', __name__)

from . import routes
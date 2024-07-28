from flask import Blueprint

# Creating blueprint for pitcher higher/lower game
pitcher_bp = Blueprint('pitcher', __name__)
from . import routes
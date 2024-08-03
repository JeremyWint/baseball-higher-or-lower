from flask import Blueprint

# Creating blueprint for strikeout higher/lower game
strikeout_bp = Blueprint('strikeout', __name__)
from . import strikeout_routes
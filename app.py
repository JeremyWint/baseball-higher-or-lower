from flask import Flask, render_template
from batter import batter_bp
from pitcher import pitcher_bp
from hitter import hitter_bp
from homer import homer_bp
from strikeout import strikeout_bp
from winner import winner_bp

app = Flask(__name__)

# Register the 'batter' blueprint with the URL prefix of '/batter'
# The 'batter_bp' blueprint contains routes related to the batter game
app.register_blueprint(batter_bp, url_prefix='/batter')

# Register the 'pitcher' blueprint with the URL prefix of '/pitcher'
# The 'pitcher_bp' blueprint contains routes related to the pitcher game
app.register_blueprint(pitcher_bp, url_prefix='/pitcher')

# Register the 'hitter' blueprint with the URL prefix of '/hitter'
# The 'hitter_bp' blueprint contains routes related to the hitter game
app.register_blueprint(hitter_bp, url_prefix='/hitter')

# Register the 'homeer' blueprint with the URL prefix of '/homer'
# The 'homer_bp' blueprint contains routes related to the homer game
app.register_blueprint(homer_bp, url_prefix='/homer')

# Register the 'strikeout' blueprint with the URL prefix of '/strikeout'
# The 'strikeout_bp' blueprint contains routes related to the strikeout game
app.register_blueprint(strikeout_bp, url_prefix='/strikeout')

# Register the 'winner' blueprint with the URL prefix of '/winner'
# The 'winner_bp' blueprint contains routes related to the winner game
app.register_blueprint(winner_bp, url_prefix='/winner')

# Define the home route for the application
@app.route('/')
def home():
    """
    Render the home page using 'index.html'.
    """
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
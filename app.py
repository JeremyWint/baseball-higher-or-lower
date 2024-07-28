from flask import Flask, render_template
from batter import batter_bp
from pitcher import pitcher_bp

app = Flask(__name__)

# Register the 'batter' blueprint with the URL prefix of '/batter'
# The 'batter_bp' blueprint contains routes related to the batter game
app.register_blueprint(batter_bp, url_prefix='/batter')

# Register the 'pitcher' blueprint with the URL prefix of '/pitcher'
# The 'pitcher_bp' blueprint contains routes related to the pitcher game
app.register_blueprint(pitcher_bp, url_prefix='/pitcher')

# Define the home route for the application
@app.route('/')
def home():
    """
    Render the home page using 'index.html'.
    """
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
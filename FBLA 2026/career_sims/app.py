from flask import Flask, render_template
from restaurant import restaurant_bp 
from trucking import trucking_bp

app = Flask(__name__)

# Register the restaurant blueprint
app.register_blueprint(trucking_bp, url_prefix='/trucking')
app.register_blueprint(restaurant_bp, url_prefix='/restaurant')

@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/trucking')
#   def trucking():
    # Placeholder for your trucking career
#    return render_template('trucking.html')

if __name__ == '__main__':
    app.run(debug=True)
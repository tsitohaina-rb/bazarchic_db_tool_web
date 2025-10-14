"""
Bazarchic Database Tool - Flask Web Application
Professional structure with blueprints and service layer
"""

import os
from flask import Flask, render_template
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Ensure required folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# Note: exports now use temporary files, no need for exports directory

# Import and register blueprints
from routes.main import main_bp
from routes.search import search_bp
from routes.images import images_bp
from routes.cloudinary import cloudinary_bp

app.register_blueprint(main_bp)
app.register_blueprint(search_bp)
app.register_blueprint(images_bp)
app.register_blueprint(cloudinary_bp)


# Error handlers
@app.errorhandler(404)
def not_found(e):
    """404 error handler"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    """500 error handler"""
    return render_template('500.html'), 500


if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    # For production deployment
    app.config['DEBUG'] = False

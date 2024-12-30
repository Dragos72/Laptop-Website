from flask import Flask
from flask_session import Session

def create_app():
    app = Flask(
        __name__,
        static_folder='../static',  # Set the static folder path relative to the app
        static_url_path='/static'   # URL path for serving static files
    )

    # Set the secret key for session management
    app.config['SECRET_KEY'] = 'your_secure_secret_key'  # Replace with a secure key in production
    app.config['SESSION_TYPE'] = 'filesystem'  # Store session data in the filesystem
    app.config['SESSION_PERMANENT'] = False    # Session will not persist after the browser is closed
    app.config['SESSION_USE_SIGNER'] = True    # Adds an additional layer of security by signing the session ID

    # Initialize Flask-Session
    Session(app)

    # Import and register blueprints
    from .routes.login import login_blueprint
    from .routes.catalog import catalog_blueprint
    from .routes.create_user import create_user_blueprint

    app.register_blueprint(login_blueprint)
    app.register_blueprint(catalog_blueprint)
    app.register_blueprint(create_user_blueprint)

    return app
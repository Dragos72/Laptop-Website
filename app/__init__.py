from flask import Flask

def create_app():
    app = Flask(
    __name__, 
    static_folder='../static',  # Set the static folder path relative to the app
    static_url_path='/static'   # URL path for serving static files
)

    # Import and register blueprints
    from .routes.login import login_blueprint
    from .routes.catalog import catalog_blueprint
    from .routes.create_user import create_user_blueprint

    app.register_blueprint(login_blueprint)
    app.register_blueprint(catalog_blueprint)
    app.register_blueprint(create_user_blueprint)

    return app
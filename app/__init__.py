from flask import Flask


def create_app() -> Flask:
    # The templates/ and static/ folders live at the project root, not inside app/.
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    # Flask signs session data with this key. We are using sessions to hold
    # lightweight chat state, so the app needs a secret key even before we add
    # a database or user accounts.
    app.config["SECRET_KEY"] = "dev-secret-key"

    from app.routes import main

    # Blueprints keep route registration separate from app creation.
    # That feels like extra structure in a small project, but it pays off once
    # the app has multiple route groups or APIs.
    app.register_blueprint(main)
    return app

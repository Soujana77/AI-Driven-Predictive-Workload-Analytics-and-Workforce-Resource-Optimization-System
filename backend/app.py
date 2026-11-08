
from flask import Flask
from flask_cors import CORS

from config import Config
from extensions import db
from routes import register_routes


def create_app():
    app = Flask(__name__)

    # Load and validate application configuration.
    app.config.from_object(Config)
    Config.validate()

    # Initialize database extension.
    db.init_app(app)

    # Enable frontend communication during development.
    CORS(app)

    # Register implemented API routes.
    register_routes(app)

    # Backend health check.
    @app.route("/api/health", methods=["GET"])
    def health():
        return {
            "status": "success",
            "message": "Workforce AI backend is running"
        }, 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=app.config["DEBUG"]
    )

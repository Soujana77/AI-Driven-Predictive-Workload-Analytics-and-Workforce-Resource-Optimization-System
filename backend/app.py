from flask import Flask
from flask_cors import CORS

from config import Config
from extensions import db


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    CORS(app)

    from routes.employee_routes import employee_bp

    app.register_blueprint(employee_bp)

    @app.route("/api/health")
    def health():
        return {
            "status": "success",
            "message": "Workforce AI backend is running"
        }

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
from pathlib import Path

from flask import Flask

from app.web.routes import contacts_bp


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(PROJECT_ROOT / "templates"),
    )

    app.register_blueprint(contacts_bp)

    return app
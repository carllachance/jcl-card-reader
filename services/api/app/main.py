from flask import Flask, jsonify

import app.models.catalog  # noqa
import app.models.inventory  # noqa
from app.api.cards import cards_blueprint
from app.core.db import Base, engine, remove_db_session


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    Base.metadata.create_all(bind=engine)
    app.register_blueprint(cards_blueprint)

    @app.teardown_appcontext
    def shutdown_session(_exception=None):
        remove_db_session()

    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

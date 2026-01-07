import os
from flask import Flask, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:test_password@localhost:5432/notes_db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    def get_current_user():
        from models import User
        uid = session.get('user_id')
        if not uid:
            return None
        return User.query.get(uid)

    @app.before_request
    def load_user():
        g.current_user = get_current_user()
    
    @app.context_processor
    def inject_user():
        return {'current_user': getattr(g, 'current_user', None)}
        
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()

    from routes.notes import notes_bp
    from routes.register import register_bp
    from routes.auth import auth_bp
    app.register_blueprint(notes_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(auth_bp)

    @app.route("/health")
    def _health():
        return {"status": "ok"}

    return app

app = create_app()
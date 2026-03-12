from flask import Flask, redirect
from eas.config import Config
from eas.extensions import db, login_manager
from eas.models.user import User
from flask_login import current_user

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from eas.auth import auth_bp
    from eas.admin import admin_bp
    from eas.lab import lab_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(lab_bp, url_prefix="/lab")

    @app.route("/")
    def home():
        if current_user.is_authenticated:
            if current_user.role == "admin":
                return redirect("/admin")
            elif current_user.role == "lab":
                return redirect("/lab")
        return redirect("/login")
    
  

    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(int(uid))

    with app.app_context():
        db.create_all()

    return app

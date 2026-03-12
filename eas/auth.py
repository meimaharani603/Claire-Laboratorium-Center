from flask import Blueprint, render_template, request, redirect, flash
from flask_login import login_user, logout_user, login_required
from eas.extensions import db
from eas.models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        user = User.query.filter_by(username=u).first()
        if user and user.check_password(p):
            login_user(user)
            return redirect("/admin" if user.is_admin() else "/lab")
        flash("Login salah")
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@auth_bp.route("/init-admin")
def init_admin():
    if User.query.filter_by(username="admin").first():
        return "Admin sudah ada"
    a = User(username="admin", role="admin")
    a.set_password("admin123")
    db.session.add(a)
    db.session.commit()
    return "Admin dibuat"

@auth_bp.route("/init-lab")
def init_lab():
    from eas.models.user import User
    from eas.extensions import db

    if User.query.filter_by(username="lab").first():
        return "Petugas sudah ada"

    u = User(username="lab", role="lab")
    u.set_password("lab123")
    db.session.add(u)
    db.session.commit()
    return "Petugas dibuat: lab / lab123"

@auth_bp.route("/debug-user")
def debug_user():
    from eas.models.user import User
    data = User.query.all()
    return "<br>".join([f"{u.id} - {u.username} - {u.role}" for u in data])

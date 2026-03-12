from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from eas.extensions import db
from eas.models.user import User
from eas.models.testcatalog import TestCatalog
from eas.models.order import Order       # diperlukan untuk dashboard


admin_bp = Blueprint("admin", __name__)


# =====================================================
#   VALIDASI HANYA ADMIN
# =====================================================
def admin_only():
    return current_user.is_authenticated and current_user.is_admin()


# =====================================================
#   DASHBOARD BARU
# =====================================================
@admin_bp.route("/")
@login_required
def dashboard():
    if not admin_only():
        return redirect("/login")

    users_count = User.query.count()
    tests_count = TestCatalog.query.count()
    orders_count = Order.query.count()

    # ⬇️ INI YANG KURANG: ambil daftar katalog tes
    tests = TestCatalog.query.order_by(TestCatalog.name.asc()).all()

    return render_template(
        "admin/dashboard.html",
        users_count=users_count,
        tests_count=tests_count,
        orders_count=orders_count,
        tests=tests,        
        active="dashboard"
    )


# =====================================================
#   USERS CRUD + MODAL
# =====================================================
@admin_bp.route("/users", methods=["GET"])
@login_required
def users_list():
    if not admin_only():
        return redirect("/login")

    users = User.query.all()

    modal = request.args.get("modal")
    edit_user = None

    if modal in ["edit", "delete"]:
        uid = request.args.get("id")
        edit_user = User.query.get(uid)

    return render_template(
        "admin/users_list.html",
        users=users,
        modal=modal,
        edit_user=edit_user,
        active="users"
    )


@admin_bp.route("/users/create", methods=["POST"])
@login_required
def users_create():
    if not admin_only():
        return redirect("/login")

    u = User(
        username=request.form["username"],
        role=request.form["role"]
    )
    u.set_password(request.form["password"])

    db.session.add(u)
    db.session.commit()
    flash("User berhasil dibuat", "success")

    return redirect("/admin/users")


@admin_bp.route("/users/update/<int:id>", methods=["POST"])
@login_required
def users_update(id):
    if not admin_only():
        return redirect("/login")

    u = User.query.get_or_404(id)
    u.username = request.form["username"]
    u.role = request.form["role"]

    if request.form["password"]:
        u.set_password(request.form["password"])

    db.session.commit()
    flash("User berhasil diperbarui", "success")

    return redirect("/admin/users")


@admin_bp.route("/users/delete/<int:id>", methods=["POST"])
@login_required
def users_delete(id):
    if not admin_only():
        return redirect("/login")

    u = User.query.get_or_404(id)
    db.session.delete(u)
    db.session.commit()
    flash("User berhasil dihapus", "success")

    return redirect("/admin/users")


# =====================================================
#   TEST CATALOG CRUD + MODAL
# =====================================================
@admin_bp.route("/tests", methods=["GET"])
@login_required
def tests_list():
    if not admin_only():
        return redirect("/login")

    tests = TestCatalog.query.all()

    modal = request.args.get("modal")
    edit_test = None

    if modal in ["edit", "delete"]:
        tid = request.args.get("id")
        edit_test = TestCatalog.query.get(tid)

    return render_template(
        "admin/tests_list.html",
        tests=tests,
        modal=modal,
        edit_test=edit_test,
        active="tests"
    )


@admin_bp.route("/tests/create", methods=["POST"])
@login_required
def tests_create():
    if not admin_only():
        return redirect("/login")

    t = TestCatalog(
        code=request.form["code"],
        name=request.form["name"],
        description=request.form["description"],
        price=request.form["price"],
        active=("active" in request.form)
    )

    db.session.add(t)
    db.session.commit()
    flash("Tes berhasil dibuat", "success")

    return redirect("/admin/tests")


@admin_bp.route("/tests/update/<int:id>", methods=["POST"])
@login_required
def tests_update(id):
    if not admin_only():
        return redirect("/login")

    t = TestCatalog.query.get_or_404(id)

    t.code = request.form["code"]
    t.name = request.form["name"]
    t.description = request.form["description"]
    t.price = request.form["price"]
    t.active = ("active" in request.form)

    db.session.commit()
    flash("Tes berhasil diperbarui", "success")

    return redirect("/admin/tests")


@admin_bp.route("/tests/delete/<int:id>", methods=["POST"])
@login_required
def tests_delete(id):
    if not admin_only():
        return redirect("/login")

    t = TestCatalog.query.get_or_404(id)

    db.session.delete(t)
    db.session.commit()
    flash("Tes berhasil dihapus", "success")

    return redirect("/admin/tests")

@admin_bp.route("/tests/toggle/<int:id>", methods=["POST"])
@login_required
def tests_toggle(id):
    if not admin_only():
        return redirect("/login")

    t = TestCatalog.query.get_or_404(id)
    t.active = not t.active
    db.session.commit()
    return {"success": True, "status": t.active}

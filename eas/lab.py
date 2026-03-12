from flask import Blueprint, render_template, request, redirect, flash
from flask_login import login_required, current_user
from eas.extensions import db
from eas.models.patient import Patient
from eas.models.testcatalog import TestCatalog
from eas.models.order import Order
from eas.models.order_item import OrderItem
from datetime import datetime

lab_bp = Blueprint("lab", __name__)


# ============================================================
# ACCESS CONTROL: LAB + ADMIN
# ============================================================
def lab_only():
    return current_user.is_authenticated and current_user.role in ("lab", "admin")


# ============================================================
# AUTO-GENERATE MRN → MRN-YYYYMMDD-XXXX
# ============================================================
def generate_mrn():
    today = datetime.now().strftime("%Y%m%d")
    total = Patient.query.count() + 1
    return f"MRN-{today}-{str(total).zfill(4)}"


# ============================================================
# AUTO-GENERATE ORDER NUMBER → ORD-YYYYMMDD-XXXX
# ============================================================
def generate_order_number():
    today = datetime.now().strftime("%Y%m%d")
    total = Order.query.count() + 1
    return f"ORD-{today}-{str(total).zfill(4)}"


# ============================================================
# DASHBOARD LAB
# ============================================================
@lab_bp.route("/")
@login_required
def dashboard():
    if not lab_only():
        return redirect("/login")
    return render_template("lab/dashboard.html")


# ============================================================
# LIST PASIEN
# ============================================================
@lab_bp.route("/patients")
@login_required
def patients_list():
    if not lab_only():
        return redirect("/login")

    patients = Patient.query.order_by(Patient.id.desc()).all()

    modal = request.args.get("modal")
    edit_patient = None

    if modal in ["edit", "delete"]:
        pid = request.args.get("id")
        edit_patient = Patient.query.get(pid)

    return render_template(
        "lab/patients_list.html",
        patients=patients,
        modal=modal,
        edit_patient=edit_patient,
        generated_mrn=generate_mrn()
    )


# ============================================================
# CREATE PASIEN
# ============================================================
@lab_bp.route("/patients/create", methods=["POST"])
@login_required
def patients_create():
    if not lab_only(): 
        return redirect("/login")

    p = Patient(
        medical_record_number=generate_mrn(),
        name=request.form["name"],
        birth_date=request.form["birth_date"],
        gender=request.form["gender"],
        address=request.form["address"],
        phone=request.form["phone"],
    )

    db.session.add(p)
    db.session.commit()

    flash("Pasien berhasil ditambahkan", "success")
    return redirect("/lab/patients")


# ============================================================
# UPDATE PASIEN
# ============================================================
@lab_bp.route("/patients/update/<int:id>", methods=["POST"])
@login_required
def patients_update(id):
    if not lab_only(): return redirect("/login")

    p = Patient.query.get_or_404(id)

    p.name = request.form["name"]
    p.birth_date = request.form["birth_date"]
    p.gender = request.form["gender"]
    p.address = request.form["address"]
    p.phone = request.form["phone"]

    db.session.commit()
    flash("Data pasien berhasil diperbarui", "success")

    return redirect("/lab/patients")


# ============================================================
# DELETE PASIEN
# ============================================================
@lab_bp.route("/patients/delete/<int:id>", methods=["POST"])
@login_required
def patients_delete(id):
    if not lab_only(): return redirect("/login")

    p = Patient.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()

    flash("Pasien berhasil dihapus", "success")
    return redirect("/lab/patients")


# ============================================================
# LIST ORDER
# ============================================================
@lab_bp.route("/orders")
@login_required
def orders_list():
    if not lab_only(): return redirect("/login")

    orders = Order.query.order_by(Order.id.desc()).all()
    patients = Patient.query.all()
    tests = TestCatalog.query.filter_by(active=True).all()

    modal = request.args.get("modal")
    selected_order = None
    selected_item = None

    if modal in ["edit", "delete", "additem"]:
        oid = request.args.get("order_id")
        selected_order = Order.query.get(oid)

    if modal == "deleteitem":
        item_id = request.args.get("item_id")
        selected_item = OrderItem.query.get(item_id)
        if selected_item:
            selected_order = selected_item.order

    return render_template(
        "lab/orders_list.html",
        orders=orders,
        patients=patients,
        tests=tests,
        modal=modal,
        new_order_number=generate_order_number(),
        selected_order=selected_order,
        selected_item=selected_item
    )


# ============================================================
# CREATE ORDER
# ============================================================
@lab_bp.route("/orders/create", methods=["POST"])
@login_required
def orders_create():
    if not lab_only(): return redirect("/login")

    o = Order(
        order_number=request.form["order_number"],
        patient_id=request.form["patient_id"]
    )

    db.session.add(o)
    db.session.commit()

    for test_id in request.form.getlist("tests"):
        db.session.add(OrderItem(order_id=o.id, test_id=test_id))

    db.session.commit()
    flash("Order berhasil dibuat", "success")

    return redirect("/lab/orders")


# ============================================================
# UPDATE ORDER (TIDAK MENYENTUH TES)
# ============================================================
@lab_bp.route("/orders/update/<int:id>", methods=["POST"])
@login_required
def orders_update(id):
    if not lab_only(): return redirect("/login")

    o = Order.query.get_or_404(id)
    o.patient_id = request.form["patient_id"]

    db.session.commit()
    flash("Order berhasil diperbarui", "success")
    return redirect("/lab/orders")


# ============================================================
# DELETE ORDER
# ============================================================
@lab_bp.route("/orders/delete/<int:id>", methods=["POST"])
@login_required
def orders_delete(id):
    if not lab_only(): return redirect("/login")

    o = Order.query.get_or_404(id)
    db.session.delete(o)
    db.session.commit()

    flash("Order berhasil dihapus", "success")
    return redirect("/lab/orders")


# ============================================================
# KELola TES DI ORDER (RESET DAN INSERT ULANG)
# ============================================================
@lab_bp.route("/orders/<int:order_id>/items/create", methods=["POST"])
@login_required
def order_items_create(order_id):
    if not lab_only(): return redirect("/login")

    o = Order.query.get_or_404(order_id)

    # Hapus semua dulu
    OrderItem.query.filter_by(order_id=o.id).delete()

    # Tambah ulang
    for test_id in request.form.getlist("tests"):
        db.session.add(OrderItem(order_id=o.id, test_id=test_id))

    db.session.commit()
    flash("Tes berhasil diperbarui", "success")

    return redirect(f"/lab/orders?modal=edit&order_id={order_id}")


# ============================================================
# DELETE SATU TES DARI ORDER
# ============================================================
@lab_bp.route("/orders/<int:order_id>/items/<int:item_id>/delete", methods=["POST"])
@login_required
def order_items_delete(order_id, item_id):
    if not lab_only(): return redirect("/login")

    item = OrderItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()

    flash("Tes berhasil dihapus", "success")
    return redirect(f"/lab/orders?modal=edit&order_id={order_id}")

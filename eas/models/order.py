from eas.extensions import db
from datetime import datetime

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(64), unique=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("Patient")
    items = db.relationship("OrderItem", backref="order", cascade="all, delete")

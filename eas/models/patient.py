from eas.extensions import db

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medical_record_number = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(128))
    birth_date = db.Column(db.String(20))
    gender = db.Column(db.String(20))
    address = db.Column(db.String(255))
    phone = db.Column(db.String(50))

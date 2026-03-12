from eas.extensions import db

class TestCatalog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(128))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    active = db.Column(db.Boolean, default=True)

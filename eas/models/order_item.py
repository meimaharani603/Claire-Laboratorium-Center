from eas.extensions import db

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    test_id = db.Column(db.Integer, db.ForeignKey("test_catalog.id"))

    test = db.relationship("TestCatalog")

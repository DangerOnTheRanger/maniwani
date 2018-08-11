from shared import db


class Session(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    slip_id = db.Column(db.Integer, db.ForeignKey("slip.id"), nullable=False)

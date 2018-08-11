from shared import db


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    bg_style = db.Column(db.String, nullable=True)
    text_style = db.Column(db.String, nullable=True)

    def to_dict(self):
        return {"name": self.name}

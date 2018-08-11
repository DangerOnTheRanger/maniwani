from shared import db

REPLY_REGEXP = r">>([0-9]+)"


class Reply(db.Model):
    reply_from = db.Column(db.Integer,
                           db.ForeignKey("post.id"),
                           nullable=False, primary_key=True)
    reply_to = db.Column(db.Integer,
                         db.ForeignKey("post.id"),
                         nullable=False,
                         primary_key=True)

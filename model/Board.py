from sqlalchemy import desc
from sqlalchemy.orm import relationship

from model.Thread import Thread
from shared import db


class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    rules = db.Column(db.String, nullable=True)
    threads = relationship("Thread", order_by=desc(Thread.last_updated))
    max_threads = db.Column(db.Integer, default=50)
    mimetypes = db.Column(db.String, nullable=False)

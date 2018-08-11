# Taken from: http://blog.mmast.net/sqlalchemy-serialize-json

from flask.json import JSONEncoder
from sqlalchemy.ext.declarative import DeclarativeMeta


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            return obj.to_dict()
        return super(CustomJSONEncoder, self).default(obj)

from flask_restful import Resource

from model.Firehose import Firehose


class FirehoseResource(Firehose, Resource):
    pass

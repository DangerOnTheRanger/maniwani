import os
import subprocess
import time
import unittest
os.environ["MANIWANI_CFG"] = "test/media-test-config.cfg"
from shared import app, db
from model.Media import storage


DOCKER_NAME = "minio-test-instance"
MINIO_START_CMD = "docker run -d -p 9000:9000 -e MINIO_ACCESS_KEY=minio -e \
MINIO_SECRET_KEY=miniostorage --name %s minio/minio server /data" % DOCKER_NAME
MINIO_STOP_CMD = "docker kill %s" % DOCKER_NAME
MINIO_REMOVE_CMD = "docker rm %s" % DOCKER_NAME
TEST_ATTACHMENT = "./test/test_img.jpg"


def minio_available():
    try:
        docker_images = str(subprocess.check_output(["docker", "images"]))
        return "minio/minio" in docker_images
    except FileNotFoundError:
        # no docker?
        return False
    
    
@unittest.skipUnless(minio_available(), "Minio not available")
class TestS3(unittest.TestCase):
    def setUp(self):
        db.create_all()
        self._start_minio()
        storage._s3_client.create_bucket(Bucket="attachments")
        storage._s3_client.create_bucket(Bucket="thumbs")
    def tearDown(self):
        subprocess.run(MINIO_STOP_CMD.split())
        subprocess.run(MINIO_REMOVE_CMD.split())
    def test_add_attachment(self):
        attachment = open(TEST_ATTACHMENT, "rb")
        # set filename attribute since werkzeug sets that on its file objects and
        # storage.save_attachment expects it to be there
        attachment.filename = attachment.name
        storage.save_attachment(attachment)
        attachment.close()
        db.session.commit()
    def _start_minio(self):
        subprocess.run(MINIO_START_CMD.split())

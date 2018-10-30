import datetime
import io
import os
import subprocess
from PIL import Image
from flask import send_from_directory, redirect
from shared import db, app


class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ext = db.Column(db.String(4), nullable=False)

    def delete_attachment(self):
        storage.delete_attachment(self.id, self.ext)


class StorageBase:
    _FFMPEG_FLAGS = "-i pipe:0 -f mjpeg -frames:v 1 -vf scale=w=500:h=500:force_original_aspect_ratio=decrease pipe:1"
    def save_attachment(self, attachment_file):
        file_ext = attachment_file.filename.rsplit('.', 1)[1].lower()
        media = Media(ext=file_ext)
        db.session.add(media)
        db.session.flush()
        media_id = media.id
        attachment_buffer = io.BytesIO(attachment_file.read())
        self._write_attachment(attachment_buffer, media_id, file_ext)
        self._write_thumbnail(self._make_thumbnail(attachment_file, media_id, file_ext), media_id)
        return media
    def bootstrap(self):
        pass
    def _make_thumbnail(self, attachment, media_id, file_ext):
        if file_ext != "webm":
            # non-webm thumbnail generation
            thumb = Image.open(attachment)
            if thumb.mode in ("RGBA", "LA"):
                background = Image.new(thumb.mode[:-1], thumb.size, (255, 255, 255))
                background.paste(thumb, thumb.split()[-1])
                thumb = background
            size = thumb.size
            scale_factor = 0
            # width > height
            if size[0] > size[1]:
                scale_factor = 500 / size[0]
            else:
                scale_factor = 500 / size[1]
            new_width = int(thumb.width * scale_factor)
            new_height = int(thumb.height * scale_factor)
            thumb = thumb.resize((new_width, new_height), Image.LANCZOS)
            thumb = thumb.convert("RGB")
            # store in temp buffer since Pillow ends up closing it
            # probably should be done in most cases, but we need an open file
            temp_buffer = io.BytesIO()
            thumb.save(temp_buffer, "JPEG")
            return io.BytesIO(temp_buffer.getvalue())
        else:
            ffmpeg_commandline = ("%s %s" % (self._get_ffmpeg_path(),
                                             self._FFMPEG_FLAGS)).split()
            attachment.seek(0)
            temp_buffer = io.BytesIO(attachment.read())
            ffmpeg_result = subprocess.run(ffmpeg_commandline,
                                           input=temp_buffer.getvalue(),
                                           stdout=subprocess.PIPE)
            return io.BytesIO(ffmpeg_result.stdout)
    def _write_attachment(self, attachment_file, media_id, media_ext):
        raise NotImplementedError
    def _write_thumbnail(self, thumbnail_bytes, media_id):
        raise NotImplementedError
    def _get_ffmpeg_path(self):
        return app.config.get("FFMPEG_PATH") or "ffmpeg"
    


class FolderStorage(StorageBase):
    _ATTACHMENT_FILENAME = "%d.%s"
    _THUMBNAIL_FILENAME = "%d.jpg"
    def __init__(self):
        super().__init__()
        self._upload_folder = app.config["UPLOAD_FOLDER"]
        self._thumb_folder = app.config["THUMB_FOLDER"]
    def get_attachment(self, media_id):
        media = db.session.query(Media).filter(Media.id == media_id).one()
        return send_from_directory(self._upload_folder,
                                   self._attachment_name(media.id, media.ext),
                                   last_modified=datetime.datetime.now())
    def get_thumbnail(self, media_id):
        return send_from_directory(self._thumb_folder,
                                   self._thumbnail_name(media_id),
                                   last_modified=datetime.datetime.now())
    def delete_attachment(self, media_id, media_ext):
        os.remove(os.path.join(self._upload_folder,
                               self._attachment_name(media_id, media_ext)))
        os.remove(os.path.join(self._thumb_folder,
                               self._thumbnail_name(media_id)))
    def bootstrap(self):
        # create upload and thumbnail directory if necessary
        if not os.path.exists("uploads/thumbs"):
            os.makedirs("uploads/thumbs")
        if not os.path.exists("uploads/attachments"):
            os.makedirs("uploads/attachments")
    def _attachment_name(self, media_id, media_ext):
        return self._ATTACHMENT_FILENAME % (media_id, media_ext)
    def _thumbnail_name(self, media_id):
        return self._THUMBNAIL_FILENAME % media_id
    def _write_attachment(self, attachment_bytes, media_id, media_ext):
        full_path = os.path.join(self._upload_folder,
                                 self._attachment_name(media_id, media_ext))
        open(full_path, "wb").write(attachment_bytes.getvalue())
    def _write_thumbnail(self, thumbnail_bytes, media_id):
        full_path = os.path.join(self._thumb_folder,
                                 self._thumbnail_name(media_id))
        open(full_path, "wb").write(thumbnail_bytes.getvalue())


class S3Storage(StorageBase):
    _ATTACHMENT_KEY = "%d.%s"
    _ATTACHMENT_BUCKET = "attachments"
    _THUMBNAIL_KEY = "%d.jpg"
    _THUMBNAIL_BUCKET = "thumbs"
    
    def __init__(self):
        self._endpoint = app.config.get("S3_ENDPOINT")
        self._access_key = app.config["S3_ACCESS_KEY"]
        self._secret_key = app.config["S3_SECRET_KEY"]
        self._s3_client = boto3.client("s3",
                                       endpoint_url = self._endpoint,
                                       aws_access_key_id = self._access_key,
                                       aws_secret_access_key = self._secret_key)

    def get_attachment(self, media_id):
        media = db.session.query(Media).filter(Media.id == media_id).one()
        media_ext = media.ext
        s3_key = self._s3_attachment_key(media_id, media_ext)
        media_url = self._s3_presigned_url(self._ATTACHMENT_BUCKET, s3_key)
        return redirect(media_url)
    def get_thumbnail(self, media_id):
        s3_key = self._s3_thumbnail_key(media_id)
        thumb_url = self._s3_presigned_url(self._THUMBNAIL_BUCKET, s3_key)
        return redirect(thumb_url)
    def delete_attachment(self, media_id, media_ext):
        s3_attach_key = self._s3_attachment_key(media_id, media_ext)
        self._s3_remove_key(self._ATTACHMENT_BUCKET, s3_attach_key)
        s3_thumb_key = self._s3_thumbnail_key(media_id)
        self._s3_remove_key(self._THUMBNAIL_BUCKET, s3_thumb_key)
    def bootstrap(self):
        self._s3_client.create_bucket(Bucket=self._ATTACHMENT_BUCKET)
        self._s3_client.create_bucket(Bucket=self._THUMBNAIL_BUCKET)
    def _write_attachment(self, attachment_file, media_id, media_ext):
        s3_key = self._s3_attachment_key(media_id, media_ext)
        self._s3_client.upload_fileobj(attachment_file, self._ATTACHMENT_BUCKET, s3_key)
    def _write_thumbnail(self, thumbnail_bytes, media_id):
        s3_key = self._s3_thumbnail_key(media_id)
        self._s3_client.upload_fileobj(thumbnail_bytes, self._THUMBNAIL_BUCKET, s3_key)
    def _s3_presigned_url(self, bucket, key):
        return self._s3_client.generate_presigned_url(ClientMethod="get_object",
                                                      Params={
                                                          "Bucket": bucket,
                                                          "Key": key
                                                      })
    def _s3_remove_key(self, bucket, key):
        self._s3_client.delete_object(Bucket=bucket, Key=key)
    def _s3_attachment_key(self, media_id, media_ext):
        return self._ATTACHMENT_KEY % (media_id, media_ext)
    def _s3_thumbnail_key(self, media_id):
        return self._THUMBNAIL_KEY % (media_id)


def get_storage_provider():
    if app.config.get("STORAGE_PROVIDER") is None:
        return FolderStorage()
    if app.config["STORAGE_PROVIDER"] == "S3":
        # prevent non-s3 installations from needing to pull in boto3
        global boto3
        boto3 = __import__("boto3")
        return S3Storage()
    elif app.config["STORAGE_PROVIDER"] == "FOLDER":
        return FolderStorage()
    # TODO: proper error-handling on unknown key value
storage = get_storage_provider()

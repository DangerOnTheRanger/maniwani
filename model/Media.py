import datetime
import io
import os
from PIL import Image
from flask import send_from_directory
from shared import db, app


class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ext = db.Column(db.String(4), nullable=False)


class StorageBase:
    def save_attachment(self, attachment_file):
        file_ext = attachment_file.filename.rsplit('.', 1)[1].lower()
        media = Media(ext=file_ext)
        db.session.add(media)
        db.session.flush()
        media_id = media.id
        self._write_attachment(attachment_file, media_id, file_ext)
        self._write_thumbnail(self._make_thumbnail(attachment_file, media_id, file_ext), media_id)
        return media
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
            thumb_contents = io.BytesIO()
            thumb.save(thumb_contents, "JPEG")
            print(thumb_contents)
            return thumb_contents
        else:
            # FIXME: webm thumbnail generation
            pass
    def _write_attachment(self, attachment_file, media_id, media_ext):
        raise NotImplementedError
    def _write_thumbnail(self, thumbnail_bytes, media_id):
        raise NotImplementedError


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

    def _attachment_name(self, media_id, media_ext):
        return self._ATTACHMENT_FILENAME % (media_id, media_ext)
    def _thumbnail_name(self, media_id):
        return self._THUMBNAIL_FILENAME % media_id
    def _write_attachment(self, attachment_file, media_id, media_ext):
        full_path = os.path.join(self._upload_folder,
                                 self._attachment_name(media_id, media_ext))
        attachment_file.save(full_path)
    def _write_thumbnail(self, thumbnail_bytes, media_id):
        full_path = os.path.join(self._thumb_folder,
                                 self._thumbnail_name(media_id))
        open(full_path, "wb").write(thumbnail_bytes.getvalue())


def get_storage_provider():
    return FolderStorage()
storage = get_storage_provider()

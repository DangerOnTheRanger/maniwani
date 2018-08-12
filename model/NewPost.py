import os
import re

from PIL import Image
from flask import current_app, request
from flask_restful import reqparse, inputs

from model.Media import Media
from model.Poster import Poster
from model.Post import Post
from model.Reply import Reply, REPLY_REGEXP
from model.Thread import Thread
from model.Slip import get_slip
from shared import db, ip_to_int, gen_poster_id


class NewPost:
    def post(self, thread_id):
        parser = reqparse.RequestParser()
        parser.add_argument("subject", type=str)
        parser.add_argument("body", type=str, required=True)
        parser.add_argument("useslip", type=inputs.boolean)
        parser.add_argument("spoiler", type=inputs.boolean)
        args = parser.parse_args()
        ip = ip_to_int(request.environ["REMOTE_ADDR"])
        poster = db.session.query(Poster).filter_by(thread=thread_id, ip_address=ip).first()
        body = args["body"]
        should_bump = False
        if poster is None:
            poster_hex = gen_poster_id()
            poster = Poster(hex_string=poster_hex, ip_address=ip, thread=thread_id)
            db.session.add(poster)
            db.session.commit()
            # bump thread if the poster hasn't posted in this thread before
            should_bump = True
        if args.get("useslip") is True:
            slip = get_slip()
            if slip and (slip.is_admin or slip.is_mod):
                poster.slip = slip.id
                db.session.add(poster)
                db.session.commit()
        media_id = None
        if "media" in request.files and request.files["media"].filename:
            uploaded_file = request.files["media"]
            file_ext = uploaded_file.filename.rsplit('.', 1)[1].lower()
            media = Media(ext=file_ext)
            db.session.add(media)
            db.session.commit()
            media_id = media.id
            full_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "%d.%s" % (media_id, file_ext))
            uploaded_file.save(full_path)
            if file_ext != "webm":
                # non-webm thumbnail generation
                thumb = Image.open(full_path)
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
                thumb.convert("RGB").save(os.path.join(current_app.config["THUMB_FOLDER"], "%d.jpg" % media_id), "JPEG")
            else:
                # FIXME: webm thumbnail generation
                pass
        post = Post(body=body, subject=args["subject"], thread=thread_id, poster=poster.id, media=media_id,
                    spoiler=args["spoiler"])
        db.session.add(post)
        db.session.commit()
        replying = re.finditer(REPLY_REGEXP, body)
        if replying:
            for match in replying:
                for raw_reply_id in match.groups():
                    reply_id = int(raw_reply_id)
                    reply = Reply(reply_from=post.id, reply_to=reply_id)
                    db.session.add(reply)
                    db.session.commit()
        if should_bump:
            thread = db.session.query(Thread).filter_by(id=thread_id).one()
            thread.last_updated = post.datetime
            db.session.commit()

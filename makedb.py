import os
from app import db, Board, Tag, gen_slip
db.create_all()
# set up some boards
for board_name in ("anime", "tech", "meta", "politics", "gaming", "music"):
    board = Board(name=board_name)
    db.session.add(board)
# admin credentials generation
admin = gen_slip("admin", "admin")
admin.is_admin = True
db.session.add(admin)
# special tags
for tag_name, bg_style, text_style in (("general", "bg-secondary", "text-light"),):
    tag = Tag(name=tag_name, bg_style=bg_style, text_style=text_style)
    db.session.add(tag)
db.session.commit()
# write a secret so we can have session support
open("secret", "w").write(str(os.urandom(16)))
# create upload and thumbnail directory if necessary
if not os.path.exists("uploads/thumb"):
    os.makedirs("uploads/thumb")

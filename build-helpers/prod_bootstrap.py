from model.Board import Board
from model.Slip import gen_slip
from model.Tag import Tag
import model.Media
import model.Poster
from shared import db

db.create_all()

# set up some boards
for board_name in ("anime", "tech", "meta", "politics", "gaming", "music"):
    board = Board(name=board_name)
    db.session.add(board)
# admin credentials generation
for slip_name, slip_pass, is_admin in (("admin", "admin", True),):
    slip = gen_slip(slip_name, slip_pass)
    slip.is_admin = is_admin
    db.session.add(slip)
# special tags
for tag_name, bg_style, text_style in (("general", "bg-secondary", "text-light"),):
    tag = Tag(name=tag_name, bg_style=bg_style, text_style=text_style)
    db.session.add(tag)
db.session.commit()
# write a secret so we can have session support

open("secret", "w").write(str(os.urandom(16)))

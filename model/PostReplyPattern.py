from sqlalchemy.orm.exc import NoResultFound
from xml import etree

from flask import url_for
from markdown.util import etree
from markdown.inlinepatterns import Pattern

from model.Reply import REPLY_REGEXP


def url_for_post(post_id):
    from model.Thread import Thread
    thread = Thread.query.filter(Thread.posts.any(id=post_id)).one()
    return url_for("threads.view", thread_id=thread.id) + "#" + str(post_id)


class PostReplyPattern(Pattern):
    def __init__(self, markdown_instance=None):
        super().__init__(REPLY_REGEXP, markdown_instance)

    def handleMatch(self, match):
        try:
            link = etree.Element("a")
            reply_id = int(match.group(2))
            link.attrib["href"] = url_for_post(reply_id)
            link.text = "&gt;&gt;%s" % reply_id
            return link
        except NoResultFound:
            dead_reply = etree.Element("span")
            reply_id = int(match.group(2))
            dead_reply.text = "&gt;&gt;%s" % reply_id
            dead_reply.attrib["class"] = "text-danger"
            return dead_reply

from xml import etree

from flask import url_for
from markdown.util import etree
from markdown.inlinepatterns import Pattern

#from .Post import url_for_post
from model.Reply import REPLY_REGEXP


def url_for_post(post_id):
    from model.Thread import Thread
    thread = Thread.query.filter(Thread.posts.any(id=post_id)).one()
    return url_for("view_thread", thread_id=thread.id) + "#" + str(post_id)


class PostReplyPattern(Pattern):
    def __init__(self, markdown_instance=None):
        super().__init__(REPLY_REGEXP, markdown_instance)

    def handleMatch(self, match):
        link = etree.Element("a")
        reply_id = int(match.group(2))
        link.attrib["href"] = url_for_post(reply_id)
        link.text = "&gt;&gt;%s" % reply_id
        return link

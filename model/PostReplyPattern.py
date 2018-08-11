from xml import etree

from markdown.inlinepatterns import Pattern

from model.Post import url_for_post
from model.Reply import REPLY_REGEXP


class PostReplyPattern(Pattern):
    def __init__(self, markdown_instance=None):
        super().__init__(REPLY_REGEXP, markdown_instance)

    def handleMatch(self, match):
        link = etree.Element("a")
        reply_id = int(match.group(2))
        link.attrib["href"] = url_for_post(reply_id)
        link.text = "&gt;&gt;%s" % reply_id
        return link

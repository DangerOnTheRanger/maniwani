from sqlalchemy.orm.exc import NoResultFound
from xml import etree

from flask import url_for
from markdown.util import etree
from markdown.inlinepatterns import Pattern

import cache
from model.Reply import REPLY_REGEXP


def post_url_cache_key(post_id):
    return "post-url-%d" % post_id


def url_for_post(post_id):
    cache_key = post_url_cache_key(post_id)
    cache_connection = cache.Cache()
    cached_url = cache_connection.get(cache_key)
    if cached_url:
        return cached_url
    from model.Thread import Thread
    thread = Thread.query.filter(Thread.posts.any(id=post_id)).one()
    post_url = url_for("threads.view", thread_id=thread.id) + "#" + str(post_id)
    cache_connection.set(cache_key, post_url)
    return post_url


class PostReplyPattern(Pattern):
    def __init__(self, markdown_instance=None):
        super().__init__(REPLY_REGEXP, markdown_instance)

    def handleMatch(self, match):
        reply_id = int(match.group(3))
        try:
            link = etree.Element("a")
            link.attrib["href"] = url_for_post(reply_id)
            link.attrib["class"] = "post-reply"
            link.attrib["data-post-id"] = str(reply_id)
            link.attrib["data-toggle"]  = "tooltip"
            link.attrib["data-placement"] = "bottom"
            link.attrib["data-html"] = "true"
            link.attrib["title"] = "<i>Loading...</i>"
            link.attrib["data-loaded"] = "false"
            link.text = "&gt;&gt;%s" % reply_id
            return link
        except NoResultFound:
            dead_reply = etree.Element("span")
            dead_reply.text = "&gt;&gt;%s" % reply_id
            dead_reply.attrib["class"] = "text-danger"
            return dead_reply

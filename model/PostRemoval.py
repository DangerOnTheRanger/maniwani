from sqlalchemy import or_

import cache
from model.Media import Media
from model.Post import Post, post_render_cache_key, CONTEXT_THREAD, CONTEXT_CATALOG
from model.PostReplyPattern import post_url_cache_key
from model.Reply import Reply
from model.ThreadPosts import thread_posts_cache_key 
from shared import db


class PostRemoval:
    def delete(self, post_id):
        self.delete_impl(post_id)
        db.session.commit()
    def delete_impl(self, post_id):
        post = db.session.query(Post).filter(Post.id == post_id).one()
        cache_connection = cache.Cache()
        cache_connection.invalidate(post_url_cache_key(post.id))
        for context in (CONTEXT_THREAD, CONTEXT_CATALOG):
            cache_connection.invalidate(post_render_cache_key(context, post.id))
        cache_connection.invalidate(thread_posts_cache_key(post.thread))
        for reply in db.session.query(Reply).filter(or_(Reply.reply_from == post_id, Reply.reply_to == post_id)):
            db.session.delete(reply)
        media = db.session.query(Media).filter(Media.id == post.media).one()
        if media:
            media.delete_attachment()
            db.session.delete(media)
        db.session.delete(post)

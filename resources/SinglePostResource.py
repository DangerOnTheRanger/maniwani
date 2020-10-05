from flask.json import jsonify
from flask_restful import Resource

from model.Post import Post, render_individual
from model.ThreadPosts import ThreadPosts
from shared import db


class SinglePostResource(Resource):
    def get(self, post_id):
        post = Post.query.get(post_id)
        thread = post.thread
        # TODO: consider fetching only a single post instead of going through ThreadPosts
        # 999 times out of 1000 this will hit cache and be pretty fast, but it's somewhat ugly
        all_posts = ThreadPosts().retrieve(thread)
        post_json = None
        for p in all_posts:
            if p["id"] == post_id:
                post_json = p
                break
        render_individual(post_json)
        return jsonify(post_json)
        

from flask_restful import Resource

from model.ThreadPosts import ThreadPosts


class ThreadPostsResource(ThreadPosts, Resource):
    pass
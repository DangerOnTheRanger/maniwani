import functools
import json
import random
import string

import gevent
import gevent.queue
from flask import Blueprint, Response, request, stream_with_context, jsonify

import keystore
from model.Post import Post


live_blueprint = Blueprint("live", __name__)
NEW_CLIENT_EVENT = "new-client"
CLIENT_JSON_TEMPLATE = '{"threads": [], "boards": []}'


def _gen_client_id():
    return "client_" + "".join(random.choices(string.hexdigits, k=10))


def _aggregate_channel(pubsub, queue, channel):
    while True:
        message = pubsub.get_message(channel)
        queue.put((channel, message))


@live_blueprint.route("/live", methods=["GET"])
def live_firehose():
    @stream_with_context
    def client_pump():
        client_id = _gen_client_id()
        new_client_message = SSEMessage(client_id, NEW_CLIENT_EVENT)
        keystore_client = keystore.Keystore()
        keystore_client.set(client_id, CLIENT_JSON_TEMPLATE)
        yield new_client_message.encode()
        pubsub = keystore.Pubsub()
        pubsub.subscribe("new-post")
        pubsub.subscribe("new-thread")
        pubsub.subscribe("new-reply")
        sub_queue = gevent.queue.Queue()
        gevent.spawn(functools.partial(_aggregate_channel, pubsub, sub_queue, "new-post"))
        gevent.spawn(functools.partial(_aggregate_channel, pubsub, sub_queue, "new-thread"))
        gevent.spawn(functools.partial(_aggregate_channel, pubsub, sub_queue, "new-reply"))
        try:
            while True:
                try:
                    channel, raw_message = sub_queue.get(timeout=30)
                except gevent.queue.Empty:
                    # send a heartbeat every 30 seconds if we don't get any new updates
                    # to keep the reverse proxy from closing the connection 
                    ping_message = SSEMessage("", "heartbeat")
                    yield ping_message.encode()
                    continue
                message = json.loads(raw_message)
                client_filter = json.loads(keystore_client.get(client_id))
                if channel == "new-post":
                    subscribed_threads = client_filter["threads"]
                    if message["thread"] in subscribed_threads:
                        new_post_message = SSEMessage(raw_message, "new-post")
                        yield new_post_message.encode()
                elif channel == "new-thread":
                    subscribed_boards = client_filter["boards"]
                    if message["board"] in subscribed_boards:
                        new_thread_message = SSEMessage(raw_message, "new-thread")
                        yield new_thread_message.encode()
                elif channel == "new-reply":
                    reply_to = message["reply_to"]
                    reply_post = Post.query.get(reply_to)
                    subscribed_threads = client_filter["threads"]
                    for thread_id in subscribed_threads:
                        if reply_post.thread == thread_id:
                            new_reply_message = SSEMessage(raw_message, "new-reply")
                            yield new_reply_message.encode()
        except GeneratorExit:
            # client closed connection
            keystore_client.delete(client_id)
    response = Response(client_pump(), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    # prevent reverse proxy from buffering messages
    response.headers["X-Accel-Buffering"] = "no"
    return response


@live_blueprint.route("/live", methods=["POST"])
def update_firehose():
    client_request = request.get_json()
    client_id = client_request["client-id"]
    keystore_client = keystore.Keystore()
    sub_state = json.loads(keystore_client.get(client_id))
    if "subscribe" in client_request:
        if "thread" in client_request["subscribe"]:
            current_subscribed_threads = sub_state["threads"]
            new_threads = client_request["subscribe"]["thread"]
            for thread_id in new_threads:
                current_subscribed_threads.append(thread_id)
            sub_state["threads"] = current_subscribed_threads
        if "board" in client_request["subscribe"]:
            current_subscribed_boards = sub_state["boards"]
            new_boards = client_request["subscribe"]["board"]
            for board_id in new_boards:
                current_subscribed_boards.append(board_id)
            sub_state["boards"] = current_subscribed_boards
    if "unsubscribe" in client_request:
        pass # TODO
    new_sub_state = json.dumps(sub_state)
    keystore_client.set(client_id, new_sub_state)
    return jsonify(success=True)


class SSEMessage:
    def __init__(self, message, event=None):
        self._message = message
        self._event = event
    def encode(self):
        encoded_message = "data:%s\n" % self._message
        if self._event:
            encoded_message += "event:%s\n" % self._event
        encoded_message += "\n\n"
        return encoded_message

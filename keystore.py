import gevent
import gevent.event
import gevent.monkey
gevent.monkey.patch_socket()
import gevent.queue
from shared import app
import storestub


def make_redis():
     host = app.config["REDIS_HOST"]
     port = app.config.get("REDIS_PORT") or 6379
     redis = __import__("redis")
     return redis.Redis(host=host, port=port, db=0, decode_responses=True)


class Keystore:
    def __init__(self):
        backend = app.config.get("STORE_PROVIDER") or "INTERNAL"
        if backend == "REDIS":
           self._client = make_redis()
        else:
            self._client = storestub.KeystoreClient()
            self._client.connect()
    def get(self, key):
        return self._client.get(key)
    def set(self, key, value):
        self._client.set(key, value)
    def delete(self, key):
        self._client.delete(key)


class Pubsub:
    def __init__(self):
        self._backend = app.config.get("STORE_PROVIDER") or "INTERNAL"
        if self._backend == "REDIS":
            self._redis_client = make_redis()
            self._pubsub_client = self._redis_client.pubsub(ignore_subscribe_messages=True)
            self._channels = {}
            self._pump_running = False
        else:
            self._client = storestub.PubsubClient()
            self._client.connect()
    def subscribe(self, channel):
        if self._backend == "REDIS":
            self._pubsub_client.subscribe(channel)
        else:
            self._client.subscribe(channel)
    def unsubscribe(self, channel):
        if self._backend == "REDIS":
            self._pubsub_client.unsubscribe(channel)
        else:
            self._client.unsubscribe(channel)
    def publish(self, channel, message):
        if self._backend == "REDIS":
            self._redis_client.publish(channel, message)
        else:
            self._client.publish(channel, message)
    def get_message(self, channel):
        if self._backend == "REDIS":
            self._ensure_pump()
            self._ensure_channel(channel)
            return self._channels[channel].get()
        else:
            return self._client.get_message(channel)
    def _ensure_pump(self):
        if self._pump_running:
            return
        self._pump_running = True
        gevent.spawn(self._redis_pump)
    def _redis_pump(self):
        for response in self._pubsub_client.listen():
            channel = response["channel"]
            message = response["data"]
            self._ensure_channel(channel)
            self._channels[channel].put(message)
    def _ensure_channel(self, channel):
        if channel not in self._channels:
            self._channels[channel] = gevent.queue.Queue()

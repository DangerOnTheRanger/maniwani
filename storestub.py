import functools
import gevent.server
from gevent import socket
import json
import struct


KEYSTORE_PORT = 5577
KEYSTORE_GET = "get"
KEYSTORE_SET = "set"
KEYSTORE_DELETE = "delete"
PUBSUB_PORT = 5578
PUBSUB_SUBSCRIBE = "subscribe"
PUBSUB_UNSUBSCRIBE = "unsubsribe"
PUBSUB_PUBLISH = "publish"


def pack_data(data):
    return struct.pack("!I", len(data)) + bytes(data, "utf8")


def unpack_data(sock, chunk_length=4096):
    response = sock.recv(4)
    if not response:
        return None
    length_remaining = struct.unpack("!I", response)[0]
    buf = ""
    while length_remaining > 0:
        # ensure we don't accidentally grab data that may belong to a separate message
        recv_amount = min(length_remaining, chunk_length)
        buf += str(sock.recv(recv_amount), "utf8")
        length_remaining -= recv_amount
    return buf


class KeystoreBackend:
    def __init__(self):
        self._values = {}
    def get(self, key):
        return self._values[key]
    def set(self, key, value):
        self._values[key] = value
    def delete(self, key):
        del self._values[key]


class PubsubBackend:
    def __init__(self):
        self._clients = {}
        self._channels = {}
    def subscribe(self, channel, client):
        if self._channels.get(channel) is None:
            self._channels[channel] = []
        self._channels[channel].append(client.client_id)
        self._clients[client.client_id] = client
    def unsubscribe(self, channel, client):
        try:
            self._channels[channel].remove(client.client_id)
        # no-op if the channel doesn't exist/client wasn't subbed
        except KeyError:
            pass
        except ValueError:
            pass
    def publish(self, channel, publishing_client, message):
        if channel not in self._channels:
            # no-op on non-existent channel
            return
        client_payload = {"channel": channel, "message": message}
        for client_id in self._channels[channel][:]:
            client = self._clients.get(client_id)
            if client is None:
                self._channels[channel].remove(client_id)
                continue
            # don't send a message back to the client who published it
            if client is publishing_client:
                continue
            try:
                client.send(json.dumps(client_payload))
            except OSError:
                self.remove_client(client)
    def serving_client(self, client):
        return client.client_id in self._clients
    def remove_client(self, client):
        for channel in self._channels:
            self.unsubscribe(channel, client)
        del self._clients[client.client_id]


class ClientFacade:
    _next_id = 0
    def __init__(self, sock):
        self.client_id = ClientFacade._next_id
        ClientFacade._next_id += 1
        self._sock = sock
    def send(self, data):
        self._sock.sendall(pack_data(data))
    def receive(self, chunk_length=4096):
        return unpack_data(self._sock, chunk_length)


def handle_keystore(keystore, sock, address):
    client = ClientFacade(sock)
    while True:
        response = client.receive()
        if response is None:
            break
        json_response = json.loads(response)
        client_payload = {}
        if json_response["cmd"] == KEYSTORE_GET:
            key = json_response["key"]
            try:
                client_payload["value"] = keystore.get(key)
            except KeyError:
                client_payload["value"] = None
            packed_payload = json.dumps(client_payload)
            try:
                client.send(packed_payload)
            except OSError:
                break
        elif json_response["cmd"] == KEYSTORE_SET:
            key = json_response["key"]
            value = json_response["value"]
            keystore.set(key, value)
        elif json_response["cmd"] == KEYSTORE_DELETE:
            key = json_response["key"]
            keystore.delete(key)


def handle_pubsub(pubsub, sock, address):
    client = ClientFacade(sock)
    while True:
        response = unpack_data(sock)
        if response is None:
            if pubsub.serving_client(client):
                pubsub.remove_client(client)
            break
        json_response = json.loads(response)
        client_payload = {}
        if json_response["cmd"] == PUBSUB_SUBSCRIBE:
            channel = json_response["channel"]
            pubsub.subscribe(channel, client)
        elif json_response["cmd"] == PUBSUB_UNSUBSCRIBE:
            channel = json_response["channel"]
            pubsub.unsubscribe(channel, client)
        elif json_response["cmd"] == PUBSUB_PUBLISH:
            channel = json_response["channel"]
            message = json_response["message"]
            pubsub.publish(channel, client, message)


class ClientBase:
    def _send_dict(self, payload):
        packed_payload = pack_data(json.dumps(payload))
        self._socket.sendall(packed_payload)


class KeystoreClient(ClientBase):
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def connect(self):
        self._socket.connect(("127.0.0.1", KEYSTORE_PORT))
    def get(self, key):
        server_payload = {"cmd": KEYSTORE_GET, "key": key}
        self._send_dict(server_payload)
        server_response = unpack_data(self._socket)
        server_json = json.loads(server_response)
        return server_json["value"]
    def set(self, key, value):
        server_payload = {"cmd": KEYSTORE_SET, "key": key, "value": value}
        self._send_dict(server_payload)
    def delete(self, key):
        server_payload = {"cmd": KEYSTORE_DELETE, "key": key}
        self._send_dict(server_payload)


class PubsubClient(ClientBase):
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._channels = {}
    def connect(self):
        self._socket.connect(("127.0.0.1", PUBSUB_PORT))
        # spawn greenlet to watch for incoming messages
        gevent.spawn(self._monitor)
    def subscribe(self, channel):
        server_payload = {"cmd": PUBSUB_SUBSCRIBE, "channel": channel}
        self._send_dict(server_payload)
        self._verify_channel(channel)
    def unsubscribe(self, channel):
        del self._channels[channel]
        server_payload = {"cmd": PUBSUB_UNSUBSCRIBE, "channel": channel}
        self._send_dict(server_payload)
    def publish(self, channel, message):
        server_payload = {"cmd": PUBSUB_PUBLISH, "channel": channel, "message": message}
        self._send_dict(server_payload)
        self._verify_channel(channel)
    def get_message(self, channel, block=True, timeout=None):
        return self._channels[channel].get(block, timeout)
    def _monitor(self):
        while True:
            server_response = unpack_data(self._socket)
            server_json = json.loads(server_response)
            channel = server_json["channel"]
            message = server_json["message"]
            self._queue_message(channel, message)
    def _queue_message(self, channel, message):
        self._verify_channel(channel)
        self._channels[channel].put(message)
    def _verify_channel(self, channel):
        if channel not in self._channels:
            self._channels[channel] = gevent.queue.Queue()


def main():
    keystore_backend = KeystoreBackend()
    keystore_handler = functools.partial(handle_keystore, keystore_backend)
    keystore_server = gevent.server.StreamServer(("127.0.0.1", KEYSTORE_PORT), keystore_handler)
    keystore_server.start()
    pubsub_backend = PubsubBackend()
    pubsub_handler = functools.partial(handle_pubsub, pubsub_backend)
    pubsub_server = gevent.server.StreamServer(("127.0.0.1", PUBSUB_PORT), pubsub_handler) 
    pubsub_server.serve_forever()


if __name__ == "__main__":
    main()

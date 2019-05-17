import keystore


class Cache:
    def __init__(self):
        self._keystore = keystore.Keystore()
    def get(self, key):
        if self._keystore.exists(key) is False:
            return None
        return self._keystore.get(key)
    def set(self, key, value):
        self._keystore.set(key, value)
    def invalidate(self, key):
        if self._keystore.exists(key):
            self._keystore.delete(key)


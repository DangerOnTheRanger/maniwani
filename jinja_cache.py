import cache

import jinja2


class KeystoreCache(jinja2.BytecodeCache):
    def __init__(self):
        super().__init__()
        self._cache_connection = None
    def load_bytecode(self, bucket):
        cache_key = self._template_key(bucket.key)
        self._ensure_connection()
        cached_bytecode = self._cache_connection.get(cache_key)
        if cached_bytecode:
            bucket.bytecode_from_string(bytes(cached_bytecode, "utf-8"))
    def dump_bytecode(self, bucket):
        cache_key = self._template_key(bucket.key)
        bytecode = str(bucket.bytecode_to_string())
        self._ensure_connection()
        self._cache_connection.set(cache_key, bytecode)
    def _ensure_connection(self):
        if not self._cache_connection:
            self._cache_connection = cache.Cache()
    def _template_key(self, template_name):
        return "jinja2-template-%s" % template_name

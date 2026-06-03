import time
import threading
from typing import Any, Callable


class SimpleTTLCache:
    def __init__(self):
        self.store = {}
        self.lock = threading.Lock()

    def get(self, key: str):
        with self.lock:
            item = self.store.get(key)
            if not item:
                return None
            value, expires = item
            if expires < time.time():
                del self.store[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: int):
        with self.lock:
            self.store[key] = (value, time.time() + ttl)


cache = SimpleTTLCache()


def cached(ttl: int = 5):
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            try:
                key = f"{func.__module__}.{func.__name__}:{args}:{kwargs}"
            except Exception:
                key = f"{func.__module__}.{func.__name__}:{id(args)}"

            result = cache.get(key)
            if result is not None:
                return result

            result = func(*args, **kwargs)
            try:
                cache.set(key, result, ttl)
            except Exception:
                pass
            return result

        return wrapper

    return decorator

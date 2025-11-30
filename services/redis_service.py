import redis
import logging
from config import Config

logger = logging.getLogger(__name__)

class MockRedis:
    """
    A simple in-memory replacement for Redis to allow local development
    without a running Redis server.
    """
    def __init__(self):
        self.store = {}
        self.lists = {}
        logger.warning("!!! USING IN-MEMORY MOCK REDIS - DATA WILL BE LOST ON RESTART !!!")

    def ping(self):
        return True

    def get(self, key):
        return self.store.get(key)

    def setex(self, key, time, value):
        # Ignores 'time' (expiry) for simplicity in mock
        self.store[key] = value
        return True

    def rpush(self, key, value):
        if key not in self.lists:
            self.lists[key] = []
        self.lists[key].append(value)
        return len(self.lists[key])
    
    def lrange(self, key, start, end):
        if key not in self.lists:
            return []
        data = self.lists[key]
        
        # Handle Redis-style slicing adjustments for Python
        # Redis 'end' is inclusive, Python slice is exclusive
        if end == -1:
            return data[start:]
        return data[start : end + 1]

    def expire(self, key, time):
        return True

class RedisService:
    def __init__(self):
        self.client = None
        self._connect()

    def _connect(self):
        try:
            # Try connecting to the real Redis (Azure or Local Docker)
            self.client = redis.from_url(
                Config.REDIS_CONN_STRING, 
                decode_responses=True,
                socket_timeout=5,            # Short timeout to fail fast
                socket_connect_timeout=5,
                ssl_cert_reqs=None
            )
            self.client.ping()
            logger.info("RedisService: Connected to Real Redis successfully.")
        except Exception as e:
            logger.error(f"RedisService: Connection to Real Redis failed: {e}")
            logger.info("RedisService: Falling back to In-Memory Mock Redis.")
            self.client = MockRedis()

    def get(self, key):
        if self.client:
            return self.client.get(key)
        return None

    def setex(self, key, time, value):
        if self.client:
            return self.client.setex(key, time, value)

    def rpush(self, key, value):
        if self.client:
            return self.client.rpush(key, value)
    
    def lrange(self, key, start, end):
        if self.client:
            return self.client.lrange(key, start, end)
        return []

    def expire(self, key, time):
        if self.client:
            return self.client.expire(key, time)

# Singleton instance
redis_client = RedisService()
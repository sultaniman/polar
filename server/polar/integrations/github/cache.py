import datetime
from typing import Optional
from githubkit.cache.base import BaseCache
from polar.redis import sync_redis


class RedisCache(BaseCache):
    """Redis Backed Cache"""

    def __init__(self):
        pass

    def get(self, key: str) -> Optional[str]:
        val = sync_redis.get("githubkit:" + key)
        return val if val else None

    async def aget(self, key: str) -> Optional[str]:
        return self.get(key)

    def set(self, key: str, value: str, ex: datetime.timedelta) -> None:
        sync_redis.setex("githubkit:" + key, time=ex, value=value)

    async def aset(self, key: str, value: str, ex: datetime.timedelta) -> None:
        return self.set(key, value, ex)

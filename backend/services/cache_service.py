"""
services/cache_service.py
Redis-based async caching layer (production-ready)
"""

from redis.asyncio import Redis
import json
import logging

logger = logging.getLogger(__name__)

# ── Redis Client ────────────────────────────────────────────
redis_client = Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
    socket_timeout=2,
    socket_connect_timeout=2,
)

CACHE_TTL = 300  # 5 minutes


# ── Health Check ────────────────────────────────────────────
import inspect

async def check_redis():
    try:
        result = redis_client.ping()

        # Handle both sync and async cases
        if inspect.isawaitable(result):
            result = await result

        if result:
            logger.info("Redis connected")

    except Exception as e:
        logger.warning("Redis not available: %s", e)


# ── GET CACHE ───────────────────────────────────────────────
async def get_cache(key: str):
    try:
        data = await redis_client.get(key)

        if data:
            logger.info("⚡ Redis HIT: %s", key)
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON in cache for key=%s", key)

    except Exception as e:
        logger.error("Redis GET error: %s", e)

    return None


# ── SET CACHE ───────────────────────────────────────────────
async def set_cache(key: str, value):
    try:
        await redis_client.setex(
            key,
            CACHE_TTL,
            json.dumps(value)
        )
        logger.info("Redis SET: %s", key)

    except Exception as e:
        logger.error("Redis SET error: %s", e)
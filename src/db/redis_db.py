import os
import redis
from dotenv import load_dotenv

load_dotenv()


def get_redis_client() -> redis.Redis:
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", "6379"))
    db = int(os.getenv("REDIS_DB", "0"))

    return redis.Redis(
        host=host,
        port=port,
        db=db,
        decode_responses=True,
    )
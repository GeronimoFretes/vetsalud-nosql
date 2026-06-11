from src.db.mongo import get_database
from src.db.redis_db import get_redis_client


def main():
    db = get_database()
    redis_client = get_redis_client()

    mongo_result = db.command("ping")
    redis_result = redis_client.ping()

    print("MongoDB OK:", mongo_result)
    print("Redis OK:", redis_result)


if __name__ == "__main__":
    main()
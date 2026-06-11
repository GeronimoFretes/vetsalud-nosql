from src.db.mongo import get_database
from src.db.redis_db import get_redis_client
from src.seed.load_redis import STOCK_INDEX_KEY


def main():
    db = get_database()
    redis_client = get_redis_client()

    collections = [
        "propietarios",
        "pacientes",
        "veterinarios",
        "consultas",
        "vacunaciones",
        "cirugias",
    ]

    print("MongoDB collections:")
    for collection in collections:
        count = db[collection].count_documents({})
        print(f"- {collection}: {count} documents")

    stock_count = redis_client.zcard(STOCK_INDEX_KEY)
    print(f"\nRedis stock products: {stock_count}")

    low_stock_count = len(redis_client.zrangebyscore(STOCK_INDEX_KEY, "-inf", 49))
    print(f"Redis low-stock products below 50 units: {low_stock_count}")


if __name__ == "__main__":
    main()
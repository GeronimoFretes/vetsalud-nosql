from src.seed.load_mongo import load_mongo
from src.seed.load_redis import load_redis


def main():
    load_mongo()
    load_redis()
    print("All data loaded successfully")


if __name__ == "__main__":
    main()
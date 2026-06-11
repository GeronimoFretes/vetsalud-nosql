from pathlib import Path

import pandas as pd

from src.db.redis_db import get_redis_client
from src.seed.extra_data import EXTRA_STOCK
from src.utils.parsing import clean_str, parse_float, parse_int


RAW_DIR = Path("data/raw")
STOCK_INDEX_KEY = "idx:stock:unidades"


def product_key(id_producto: str) -> str:
    return f"stock:producto:{id_producto}"


def save_stock_product(redis_client, product: dict):
    id_producto = product["id_producto"]
    unidades = int(product["unidades"])

    redis_client.hset(product_key(id_producto), mapping=product)
    redis_client.zadd(STOCK_INDEX_KEY, {id_producto: unidades})


def load_redis():
    redis_client = get_redis_client()

    redis_client.flushdb()

    df = pd.read_csv(RAW_DIR / "stock_farmaceutico.csv")

    products = []
    for _, row in df.iterrows():
        products.append(
            {
                "id_producto": clean_str(row["id_producto"]),
                "nombre": clean_str(row["nombre"]),
                "categoria": clean_str(row["categoria"]),
                "unidades": parse_int(row["unidades"]),
                "precio_unit": parse_float(row["precio_unit"]),
                "vencimiento": clean_str(row["vencimiento"]),
                "proveedor": clean_str(row["proveedor"]),
            }
        )

    products.extend(EXTRA_STOCK)

    for product in products:
        save_stock_product(redis_client, product)

    print("Redis loaded successfully")


if __name__ == "__main__":
    load_redis()
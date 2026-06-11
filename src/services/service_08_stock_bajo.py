from src.db.redis_db import get_redis_client
from src.seed.load_redis import STOCK_INDEX_KEY, product_key
from src.utils.json_tools import print_json, save_json


def _parse_stock_product(product: dict) -> dict:
    """
    Converts Redis string values into clearer Python types.
    Redis stores values as strings, so numeric fields are parsed here.
    """
    return {
        "id_producto": product.get("id_producto"),
        "nombre": product.get("nombre"),
        "categoria": product.get("categoria"),
        "unidades": int(product.get("unidades", 0)),
        "precio_unit": float(product.get("precio_unit", 0)),
        "vencimiento": product.get("vencimiento"),
        "proveedor": product.get("proveedor"),
    }


def get_productos_con_stock_menor_a_50():
    """
    Service 08:
    Returns pharmaceutical stock products with fewer than 50 units,
    including supplier information.

    Redis structures:
    - Hash per product: stock:producto:<id_producto>
    - Sorted set index: idx:stock:unidades

    Main operations:
    - ZRANGEBYSCORE to get product ids with units below 50
    - HGETALL to retrieve full product details
    """
    redis_client = get_redis_client()

    product_ids = redis_client.zrangebyscore(STOCK_INDEX_KEY, "-inf", 49)

    products = []
    for id_producto in product_ids:
        raw_product = redis_client.hgetall(product_key(id_producto))

        if raw_product:
            products.append(_parse_stock_product(raw_product))

    products.sort(key=lambda product: (product["unidades"], product["id_producto"]))

    return products


def main():
    result = get_productos_con_stock_menor_a_50()
    print_json(result)
    save_json("service_08_stock_bajo.json", result)


if __name__ == "__main__":
    main()
import json
from datetime import datetime
from typing import Any

from redis.exceptions import WatchError

from src.db.redis_db import get_redis_client
from src.seed.load_redis import STOCK_INDEX_KEY, product_key
from src.utils.json_tools import print_json, save_json


STOCK_MOVEMENTS_KEY = "movimientos:stock"


def _parse_stock_product(product: dict) -> dict:
    """
    Converts Redis string values into clearer Python types.
    Redis stores values as strings.
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


def _aggregate_consumos(consumos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Aggregates repeated product ids in the same stock update.

    Example:
    [
        {"id_producto": "PRX003", "cantidad": 2},
        {"id_producto": "PRX003", "cantidad": 1}
    ]

    becomes:
    [
        {"id_producto": "PRX003", "cantidad": 3}
    ]
    """
    if not consumos:
        raise ValueError("The consumos list cannot be empty")

    aggregated: dict[str, int] = {}

    for item in consumos:
        id_producto = item.get("id_producto")
        cantidad = item.get("cantidad")

        if id_producto is None or str(id_producto).strip() == "":
            raise ValueError("Every consumo must include id_producto")

        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid cantidad for product {id_producto}")

        if cantidad <= 0:
            raise ValueError(f"Cantidad must be greater than zero for product {id_producto}")

        aggregated[id_producto] = aggregated.get(id_producto, 0) + cantidad

    return [
        {
            "id_producto": id_producto,
            "cantidad": cantidad,
        }
        for id_producto, cantidad in aggregated.items()
    ]


def actualizar_stock_tras_consulta(
    id_consulta: str,
    consumos: list[dict[str, Any]],
    max_retries: int = 3,
) -> dict:
    """
    Service 15:
    Performs a massive stock update after a consultation by decrementing
    product units in Redis.

    Redis structures:
    - Hash per product: stock:producto:<id_producto>
    - Sorted set index: idx:stock:unidades
    - List of stock movements: movimientos:stock

    Validations:
    - id_consulta must be present.
    - consumed products list cannot be empty.
    - every product must exist in Redis.
    - every quantity must be positive.
    - every product must have enough stock.

    Consistency:
    - The product hash and sorted-set index are updated together.
    - WATCH/MULTI/EXEC is used to reduce the risk of concurrent stock conflicts.
    """
    if id_consulta is None or str(id_consulta).strip() == "":
        raise ValueError("id_consulta is required")

    redis_client = get_redis_client()
    consumos_agregados = _aggregate_consumos(consumos)

    watched_keys = [
        product_key(item["id_producto"])
        for item in consumos_agregados
    ]

    for attempt in range(max_retries):
        try:
            with redis_client.pipeline() as pipe:
                pipe.watch(*watched_keys)

                productos_antes = []
                updates = []

                for item in consumos_agregados:
                    id_producto = item["id_producto"]
                    cantidad = item["cantidad"]
                    key = product_key(id_producto)

                    raw_product = pipe.hgetall(key)

                    if not raw_product:
                        pipe.unwatch()
                        raise ValueError(f"Product with id_producto={id_producto} does not exist")

                    product_before = _parse_stock_product(raw_product)
                    unidades_actuales = product_before["unidades"]

                    if unidades_actuales < cantidad:
                        pipe.unwatch()
                        raise ValueError(
                            f"Insufficient stock for product {id_producto}. "
                            f"Available={unidades_actuales}, requested={cantidad}"
                        )

                    unidades_nuevas = unidades_actuales - cantidad

                    productos_antes.append(product_before)
                    updates.append(
                        {
                            "id_producto": id_producto,
                            "cantidad_decrementada": cantidad,
                            "unidades_antes": unidades_actuales,
                            "unidades_despues": unidades_nuevas,
                        }
                    )

                pipe.multi()

                fecha_movimiento = datetime.today().isoformat()

                for update in updates:
                    id_producto = update["id_producto"]
                    cantidad = update["cantidad_decrementada"]
                    unidades_despues = update["unidades_despues"]

                    pipe.hincrby(product_key(id_producto), "unidades", -cantidad)
                    pipe.zadd(STOCK_INDEX_KEY, {id_producto: unidades_despues})

                    movement = {
                        "id_consulta": id_consulta,
                        "id_producto": id_producto,
                        "cantidad_decrementada": cantidad,
                        "unidades_antes": update["unidades_antes"],
                        "unidades_despues": unidades_despues,
                        "fecha_movimiento": fecha_movimiento,
                    }

                    pipe.rpush(STOCK_MOVEMENTS_KEY, json.dumps(movement, ensure_ascii=False))

                pipe.execute()

                productos_despues = []
                for update in updates:
                    raw_after = redis_client.hgetall(product_key(update["id_producto"]))
                    productos_despues.append(_parse_stock_product(raw_after))

                return {
                    "id_consulta": id_consulta,
                    "actualizacion_exitosa": True,
                    "productos_antes": productos_antes,
                    "movimientos": updates,
                    "productos_despues": productos_despues,
                }

        except WatchError:
            if attempt == max_retries - 1:
                raise RuntimeError("Stock update failed because of concurrent modifications")

    raise RuntimeError("Stock update failed unexpectedly")


def _reset_demo_stock_values() -> None:
    """
    Resets only the demo products to known values so the example can be
    run multiple times without producing different results.

    This is only for the demonstration in main().
    The real service function does not reset stock.
    """
    redis_client = get_redis_client()

    demo_values = {
        "PRX003": 120,
        "PRX005": 200,
    }

    for id_producto, unidades in demo_values.items():
        key = product_key(id_producto)

        if redis_client.exists(key):
            redis_client.hset(key, "unidades", unidades)
            redis_client.zadd(STOCK_INDEX_KEY, {id_producto: unidades})


def main():
    """
    Demonstrates service 15 with two products consumed after a consultation.
    """
    _reset_demo_stock_values()

    result = actualizar_stock_tras_consulta(
        id_consulta="CNUEVA001",
        consumos=[
            {
                "id_producto": "PRX003",
                "cantidad": 2,
            },
            {
                "id_producto": "PRX005",
                "cantidad": 5,
            },
        ],
    )

    print_json(result)
    save_json("service_15_actualizar_stock.json", result)


if __name__ == "__main__":
    main()
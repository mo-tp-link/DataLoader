from __future__ import annotations
from .abstract_data_loader import DataLoaderABC


class AMZPriceLoader(DataLoaderABC):
    file_name = "pure_price.csv"

    str_cols = [
        "asin",
        # "cap_name",
        "product_name",
    ]

    float_cols = [
        "value"
    ]

    timestamp_cols = [
        "timestamp"
    ]

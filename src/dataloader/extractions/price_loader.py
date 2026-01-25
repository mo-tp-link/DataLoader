from __future__ import annotations
from .abstract_data_loader import DataLoaderABC


class PriceLoader(DataLoaderABC):
    str_cols = [
        "Product Name",
        "Short Product Description",
    ]

    float_cols = [
        "Disty Cost(CAD)",
        "VAD Cost(CAD)",
        "TDL Cost(CAD)",
        "KGP Cost(CAD)",
        "Ameta Cost(CAD)",
    ]

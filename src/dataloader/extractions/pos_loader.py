from __future__ import annotations

from pathlib import Path

from dataloader.utils import LoadResult

from .abstract_data_loader import DataLoaderABC


class POSLoader(DataLoaderABC):
    sheet_name = "raw data"

    date_cols = ["Invoice Date"]  # noqa: RUF012
    datetime_cols = ["Created Time"]  # noqa: RUF012
    str_cols = [  # noqa: RUF012
        "Invoice #",
        "Item Model",
        "BU",
        "Category",
        "Sub-Category",
        "Reseller",
        "Province",
        "Region",
        "Zip code",
        "Disti",
        "Account Manager",
        "Business Segment",
        "VIR Exclusion",
        "Sales Team",
        "Buy In Group",
    ]
    int_cols = [  # noqa: RUF012
        "Year",
        "Month",
        "Invoice Week",
        "Qty",
    ]
    float_cols = [  # noqa: RUF012
        "Price",
        "Amount",
    ]

    def load(self, path: str | Path | None = None, **kwargs) -> LoadResult:

        if "search_dir" not in kwargs:
            search_dir = "/mnt/c/Users/Mo/OneDrive - TP-Link/informal_TP-Link Canada B2B - General/3.1 Sales stats_POS report(B2B Gross Revenue)/"
            kwargs["search_dir"] = search_dir

        return super().load(path, **kwargs)

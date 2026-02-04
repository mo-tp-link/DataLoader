from __future__ import annotations

from .abstract_data_loader import DataLoaderABC


class POSLoader(DataLoaderABC):
    sheet_name = "raw data"

    date_cols = ["Invoice Date"]
    datetime_cols = ["Created Time"]
    str_cols = [
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
    int_cols = [
        "Year",
        "Month",
        "Invoice Week",
        "Qty",
    ]
    float_cols = [
        "Price",
        "Amount",
    ]

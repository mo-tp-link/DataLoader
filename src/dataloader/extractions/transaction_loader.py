from __future__ import annotations
from .abstract_data_loader import DataLoaderABC


class TransactionLoader(DataLoaderABC):
    file_name = "TransactionDetail.xlsx"
    header_row = 1

    date_cols = [
        "Date",
    ]
    str_cols = [
        "Source Type",
        "Order No.",
        "CI/StampNO.",
        "Item Model",
        "Item Number",
        "Item Spec",
        "Item Version",
        "Customer Class",
        "Country Code",
        "Subinventory",
        "Transaction Type",
        "Remark",
        "PO Number",
        "Customer",
        "Created By",
        "Transfer Subinventory",
        "Orgnization",
        "Destination Org",
        "PI Number",
        "HS CODE",
        "GREEN Tax ",
        "GT Category",
        "Order Date",
    ]
    int_cols = [
        "Quantity",
    ]
    float_cols = ["Weight/kg"]



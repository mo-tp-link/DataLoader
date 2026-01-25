from __future__ import annotations
from .abstract_data_loader import DataLoaderABC

class BOLoader(DataLoaderABC):
    file_name = "BackOrderList.xlsx"
    sheet_name = "BackOrderList"
    str_cols = [
        "Customer",
        "PO NO.",
        "SO NO.",
        "Item NO.",
        "Item Model",
        "Item Spec",
        "Item Version",
        "Reference Version",
        "Customer Class",
        "Price List Name",
        "Price",
        "Amount",
        "Currency",
        "BO Amount",
        "Subinventory",
        "Creator",
        "Sales Team",
        "Sales Team Reserved Qty",
        "Stock Reservation No.&Qty",
        "Credit Hold",
        "Case Packing Only",
        "Ship To Site Number",
        "Order Amount Sales Tax",
        "BO Amount Sales Tax",
        "BU",
        "Packing",
        "CTNS",
        "Tax Registration No.",
        "Origin",
        "Reserved Qty(Picked)",
        "Reserved Qty(Unpicked)",
        "Order Remark",
        "Line Remark",
        "Account No.",
        "Bill To Site Number",
    ]
    date_cols = [
        "Order Date",
        "Schedule Ship Date",
        "Request Date",
        "Latest ETA",
    ]
    int_cols = [
        "Order Qty",
        "Shipped Qty",
        "Received Qty",
        "Reserved Qty",
        "Remain Qty",
        "OnHand Qty",
        "Available Qty",
    ]


if __name__ == "__main__":
    loader = BOLoader()
    res = loader.load()

    print(res)
    print(res.frame.collect().head())
    print(res.frame.collect_schema())

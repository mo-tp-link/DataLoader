from __future__ import annotations
from .abstract_data_loader import DataLoaderABC

class InventoryLoader(DataLoaderABC):

    file_name = "InventoryInformation.xlsx"
    sheet_name = "Sheet1"
    str_cols = [
        "Item Number",
        "Item Model",
        "Item Spec",
        "Item Version",
        "Description",
        "Country Code",
        "Customer Class",
        "Business Unit",
        "Power Spec",
        "Subcategory",
        "Subinventory",
        "Inventory Organization",
        "EAN-13",
        "UPC-12",
        "Customer Name",
        "Local Attribute1",
        "Item Description",
        "Origin",
    ]
    int_cols = [
        "On-hand quantity",
        "On-hand Day",
        "Available Quantity",
        "Reservation Quantity",
        "In-transit Quantity",
        "BO Quantity",
        "Packing",
    ]

if __name__ == "__main__":
    inv_loader = InventoryLoader()
    inv_loader.load()
    res = inv_loader.load()


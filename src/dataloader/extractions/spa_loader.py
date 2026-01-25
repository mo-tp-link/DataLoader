from __future__ import annotations
from .abstract_data_loader import DataLoaderABC


class SPALoader(DataLoaderABC):
    date_cols = [
        "Expiration Date",
        "Effective Date",
    ]
    datetime_cols = [
        "Approved Date",
        "Creation Date",
    ]
    str_cols = [
        "Rebate Type",
        "Distributor",
        "Reseller Name",
        "End User",
        "Product Name",
        "SPA",
        "Distributor Rep Email",
        "Reseller Rep Email",
        "End User Email",
        "End User Vertical",
        "Applicant",
        "Applicant Email",
        "Deal Description",
        "Status",
        "Application CC",
        "Next Approver",
        "Approved By",
        "Approved Notes",
        "Content Sha",
    ]
    int_cols = [
        "Minimum Quantity",
        "Maximum Quantity",
        "Expected Quantity",
    ]
    float_cols = [
        "List Price",
        "Discount Percentage",
        "Discount Amount",
        "Pre-Load Discount",
        "Total Discount",
        "Total Discount Pctg",
        "Net Cost",
        "Deal Size",
    ]
    bool_cols = [
        "Known Item",
        "Demo",
        "One Time SPA",
    ]


if __name__ == "__main__":
    pos_loader = SPALoader()

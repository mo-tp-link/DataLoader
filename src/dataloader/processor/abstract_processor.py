import re
from abc import ABC, abstractmethod

import polars as pl

from dataloader.utils import LoadResult


class ProcessorAbstract(ABC):
    schema_cls = None
    client_code_map = {
        "ASI Computer Technologies(Canada) Corp.": "CCT",
        "TELUS Communications Inc.": "TLS",
        "STAPLES CANADA ULC": "STP",
        "Ingram Micro LP": "WMT",
        "WAL-MART CANADA CORP.": "WMT",
        "Best Buy Canada Ltd": "BBY",
        "Costco Wholesale Canada Ltd": "CSC",
        "Amazon.com.ca, Inc.": "AMZ",
    }

    @staticmethod
    def clean_cap_name(col) -> pl.Expr:
        return (
            pl.col(col)
            .str.strip_chars()
            .str.to_uppercase()
            .str.replace_all(r"[^A-Z0-9+]", "")
            .alias("cap_name")
        )

    @staticmethod
    def clean_company_name(col) -> pl.Expr:
        return (
            pl.col(col)
            .str.strip_chars()
            .str.to_uppercase()
            .str.replace_all(r"[^A-Z0-9]", "")
            .alias("cap_cust")
        )

    @staticmethod
    def clean_col_name(c):
        pattern = r"[^A-Za-z0-9]"
        return re.sub(r"_+", "_", re.sub(pattern, "_", c)).lower().strip("_")

    def psi_convertion(self):
        pass

    def clean_cat_str(self, c):
        return (
            pl.col(c)
            .str.strip_chars()
            .str.to_uppercase()
            .str.replace_all(r"[^A-Z0-9]", "")
        )

    def build_client_code(self, col) -> pl.Expr:
        return pl.col(col).replace_strict(self.client_code_map, default="GNR")

    @abstractmethod
    def process(self, lr: LoadResult | None, *args, **kwargs) -> LoadResult | None:
        pass

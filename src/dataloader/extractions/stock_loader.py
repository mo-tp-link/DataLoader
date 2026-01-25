from __future__ import annotations
import json
import polars as pl
from pathlib import Path
from datetime import datetime
from dataloader.utils import LoadResult
from .abstract_data_loader import DataLoaderABC

# TODO: Define in dataloader.utils or config module
production_stage_schedule = []


class StockLoader(DataLoaderABC):
    file_name = "output.csv"

    str_cols = [
        "product_name",
        "cap_name",
        "bu",
        "category",
        "sub_category",
        "product_line",
        "stock_assurance",
    ]

    def _convert_dates(self, batch_info: dict) -> dict:
        """Convert date string fields to Timestamp objects."""
        DATE_FIELDS = ("shipping_date", "arriving_date", "inventory_date")
        result = batch_info.copy()
        for field in DATE_FIELDS:
            if field in result and result[field] is not None:
                result[field] = datetime.strptime(result[field], "%Y-%m-%d")
        return result

    def load(self, path: str | Path | None = None, **kwargs) -> LoadResult:
        batch_path = self.data_path / "batches.json"
        tracker_path = self.data_path / "creation_date.json"

        with open(tracker_path, "r") as f:
            tracker = json.load(f)
        with open(batch_path, "r") as f:
            _batches = json.load(f)
            batch = {
                batch_id: self._convert_dates(batch_info)
                for batch_id, batch_info in _batches.items()
            }

        result = super().load(path, **kwargs)

        frame = result.frame.with_columns(
            pl.exclude(self.str_cols).cast(pl.Int64, strict=False),
            pl.col(self.str_cols)
            .fill_null("Missing")
            .str.to_uppercase()
            .str.strip_chars(),
        )
        result.frame = frame
        result.context.update(
            {
                "batch": batch,
                "tracker": tracker,
                "schedule": production_stage_schedule,
            }
        )
        return result


if __name__ == "__main__":
    from pprint import pprint

    stock = StockLoader()
    res = stock.load()

    pprint(res.frame.collect_schema())
    pprint(res.context["batch"])
    pprint(res.context["tracker"])

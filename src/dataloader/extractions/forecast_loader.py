from __future__ import annotations
from pathlib import Path

import re
import polars as pl

from dataloader.utils import LoadResult
from .abstract_data_loader import DataLoaderABC

# TODO: Define these in dataloader.utils or a config module
production_stage_schedule = []
partner_inventories = {}


class ForecastLoader(DataLoaderABC):
    file_name = "/mnt/c/Users/Mo/OneDrive - TP-Link/Keeper of the Endless Stock, Warden of the Supply Realms, Master of Replenishment, Breaker of Stockouts, Tamer of Chaos and Crates's Shared Folder/Forecast Shared.xlsx"

    str_cols = [
        "INV",
        "CLT",
        "SKU",
        "MFG#",
        "TYP",
        "Notes",
    ]
    float_cols = ["BUF"]
    int_cols = ["Presentation Stock"]

    def load(self, path: str | Path | None = None, **kwargs) -> LoadResult:
        # 1. 【复用】调用父类解决 IO 问题 (支持 CSV, Excel, Bytes, Path)
        # result 包含了初步加载的 LazyFrame 和基础 context

        # result = super().load(path, **kwargs)
        all_dfs = [
            v.lazy().with_columns(
                pl.col(self.str_cols).cast(pl.String),
                pl.col(self.float_cols)
                .cast(pl.Float64)
                .fill_null(1.0),  # FILL 1.0, not 0.0
                pl.exclude(self.str_cols + self.float_cols)
                .cast(pl.String)
                .str.strip_chars()
                .replace("", None)  # Convert empty strings to nulls
                .cast(pl.Int64)
                .fill_null(0),
            )
            for _, v in pl.read_excel(self.file_name, sheet_id=0).items()
        ]
        combined = pl.concat(
            all_dfs,
            how="diagonal",
        )
        #
        clean_frame = combined.with_columns(
            pl.col(self.str_cols)
            .fill_null("Missing")
            .str.to_uppercase()
            .str.strip_chars(),
            pl.exclude(self.str_cols + self.float_cols).cast(pl.Int64).fill_null(0),
        )
        contenxt = {
            "source": path,
            "schedule": production_stage_schedule,
            "partner_inventories": partner_inventories,
            # 如果需要覆盖父类的 source 或 loader 信息，也可以在这里改
        }

        result = LoadResult(frame=clean_frame, context=contenxt)

        return result


if __name__ == "__main__":
    loader = ForecastLoader()
    r = loader.load()
    print(r.frame.limit(5).collect().columns)

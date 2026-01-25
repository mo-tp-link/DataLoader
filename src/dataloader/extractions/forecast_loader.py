from __future__ import annotations
from pathlib import Path

import polars as pl

from dataloader.utils import LoadResult
from .abstract_data_loader import DataLoaderABC

# TODO: Define these in dataloader.utils or a config module
production_stage_schedule = []
partner_inventories = {}


class ForecastLoader(DataLoaderABC):
    file_name = "combined_fcst.csv"
    sheet_name = "combined_fcst"

    str_cols = [
        "INV",
        "CLT",
        "cap_name",
    ]

    def load(self, path: str | Path | None = None, **kwargs) -> LoadResult:
        # 1. 【复用】调用父类解决 IO 问题 (支持 CSV, Excel, Bytes, Path)
        # result 包含了初步加载的 LazyFrame 和基础 context
        result = super().load(path, **kwargs)

        clean_frame = result.frame.with_columns(
            pl.exclude(self.str_cols).cast(pl.Float64, strict=False),
            pl.col(self.str_cols)
            .fill_null("Missing")
            .str.to_uppercase()
            .str.strip_chars(),
        )

        result.context.update(
            {
                "schedule": production_stage_schedule,
                "partner_inventories": partner_inventories,
                # 如果需要覆盖父类的 source 或 loader 信息，也可以在这里改
            }
        )
        result.frame = clean_frame

        return result


if __name__ == "__main__":
    loader = ForecastLoader()
    r = loader.load()
    print(r.frame.limit(5).collect().columns)

from __future__ import annotations

import re
import polars as pl
from typing import List
from dataclasses import dataclass


@dataclass(frozen=True)
class ForecastSchema:
    id_cols: List[str]
    inv_cols: List[str]
    forecast_cols: List[str]

    @property
    def all_cols(self) -> set[str]:
        """Return all known columns in the schema."""
        return set(self.id_cols + self.inv + self.forecast_cols)


def build_forecast_schema(
    df: pl.LazyFrame,
) -> ForecastSchema:
    id_cols = ["clt", "cap_name"]
    inv_cols = ["inv"]

    schema_dict = df.collect_schema()
    all_cols = list(schema_dict.keys())
    forecast_col_patterns = r"^\d{4}_\d{2}"
    forecast_cols = [c for c in all_cols if re.match(forecast_col_patterns, c)]

    return ForecastSchema(
        id_cols=id_cols, inv_cols=inv_cols, forecast_cols=forecast_cols
    )

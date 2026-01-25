from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict
import polars as pl


@dataclass(frozen=True)
class StockPlanSchema:
    """Immutable container for all column groups used in StockPlan processing."""

    # Static columns
    id_cols: List[str]
    name_cols: List[str]
    production_cols: List[str]
    psi_cols: List[str]
    partner_cols: List[str]
    total_cols: List[str]

    # Dynamically discovered columns
    shipping_cols: List[str]
    sale_out_cols: List[str]
    on_hand_cols: List[str]
    disty_cols: List[str]
    schedule_cols: list[str]
    avg_cols : List[str]

    @property
    def all_cols(self) -> set[str]:
        """Return all known columns in the schema."""
        return set(
            self.id_cols
            + self.name_cols
            + self.production_cols
            + self.psi_cols
            + self.partner_cols
            + self.total_cols
            + self.shipping_cols
            + self.sale_out_cols
            + self.on_hand_cols
            + self.disty_cols
            + self.avg_cols
        )


def build_stockplan_schema(
    df: pl.LazyFrame,
    batches: Dict[str, Dict],
    upload_time: Dict[str, datetime] | None = None,
) -> StockPlanSchema:
    """
    Inspect a Polars LazyFrame and supplemental metadata to build a StockPlanSpec.

    Parameters
    ----------
    df : pl.LazyFrame
        Input dataframe used to infer dynamic columns.
    batches : dict
        Batch dictionary; only its keys (shipping columns) are used.
    upload_time : dict, optional
        Tracker / creation-time metadata. Not currently used, but accepted for consistency.

    Returns
    -------
    StockPlanSpec
        Frozen specification object containing all relevant column groups.
    """

    # ① Collect schema (column names only)
    schema_dict = df.collect_schema()
    all_cols = list(schema_dict.keys())

    def match_cols(pattern: str) -> list[str]:
        return [c for c in all_cols if re.match(pattern, c)]

    # ② Define static groups (known columns)
    id_cols = ["cap_name"]
    name_cols = [
        "item_model",
        "product_line",
        "bu",
        "category",
        "sub_category",
        "stock_assurance",
    ]
    production_cols = [
        "for_sea",
        "for_air",
        "hq_bo",
        "not_ready_for_delivery",
        "waiting_for_delivery",
    ]
    schedule_cols = [
        "hq_bo",
        "not_ready_for_delivery",
        "waiting_for_delivery",
    ]
    psi_cols = [
        "on_hand_quantity",
        "on_hand_day",
        "available_quantity",
        "reservation_quantity",
        "bo_quantity",
        "packing",
    ]
    partner_cols = [
        # "best_buy", # renamed to bby_on_hand
        "amazon_on_hand",
        # "amazon_in_transit", Mer
    ]
    total_cols = ["produce_transit_inventory_total"]
    average_sell_out_cols = ["avg_3_or_6_mth"]

    # ③ Infer dynamic groups (regex-based)
    sale_out_cols = match_cols(r"\d{4}_\d{1,2}")
    on_hand_cols = match_cols(r".*_on_hand$")
    disty_cols = match_cols(r".*_bo_[a-z]*_qty$|^.*transit.*$")
    shipping_cols = [ c for c in batches.keys() if c in all_cols ] if batches else []

    # ④ Return frozen spec (no heavy refs)
    return StockPlanSchema(
        id_cols=id_cols,
        name_cols=name_cols,
        production_cols=production_cols,
        psi_cols=psi_cols,
        partner_cols=partner_cols,
        total_cols=total_cols,
        shipping_cols=shipping_cols,
        sale_out_cols=sale_out_cols,
        on_hand_cols=on_hand_cols,
        disty_cols=disty_cols,
        schedule_cols=schedule_cols,
        avg_cols = average_sell_out_cols
    )

import polars as pl

from dataloader.schemas.stock_plan_schema import build_stockplan_schema
from dataloader.utils import LoadResult
from .abstract_processor import ProcessorAbstract


class StockProcessor(ProcessorAbstract):
    def process(self, lr: LoadResult, *args, **kwargs) -> LoadResult:
        batch = lr.get("batch")
        tracker = lr.get("tracker")
        tracker["dh"] = tracker["dh1"]
        out = lr.frame.rename({"product_name": "item_model"}).rename(
            self.clean_col_name
        )
        latest_update_time = max(tracker.values())
        # 2️⃣ Build schema dynamically from data + metadata
        schema = build_stockplan_schema(df=out, batches=batch, upload_time=tracker)
        new_batch = {k: v for k, v in batch.items() if k in schema.shipping_cols}

        out = (
            out.with_columns(
                pl.exclude(schema.name_cols + schema.id_cols).cast(pl.Int64),
                pl.col(schema.name_cols)
                .fill_null("Missing")
                .str.to_uppercase()
                .str.strip_chars(),
            )
            .with_columns(
                (pl.col("amazon_on_hand") + pl.col("amazon_in_transit")).alias(
                    "amazon_on_hand"
                )
            )
            .rename({"best_buy": "bby_on_hand"})
        )
        schema.on_hand_cols.append("bby_on_hand")
        cap_name_pair = out.select(["item_model", "cap_name"]).unique()
        out = out.select(schema.all_cols)
        lr.add(
            schema=schema,
            cap_name_pair=cap_name_pair,
            latest_update=latest_update_time,
            batch=new_batch,
        )

        print("Loading Stock")
        return LoadResult(frame=out, context=lr.context)

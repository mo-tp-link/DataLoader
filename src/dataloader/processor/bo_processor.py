import polars as pl
from datetime import datetime
from typing import Any

from dataloader.schemas import BackOrderSchema, StockPlanSchema
from dataloader.utils import LoadResult
from .abstract_processor import ProcessorAbstract


class BOProcessor(ProcessorAbstract):
    schema_cls = BackOrderSchema

    def calculate_bo_fulfilment(self, out, inv, stock):
        supply_dfs = []

        # --- 2.1 Process On-Hand Inventory (INV) ---
        if inv is not None:
            # Assuming InventorySchema has 'available_quantity'
            inv_frame = inv.frame.select(
                ["cap_name", "available_quantity", "subinventory"]
            ).rename({"available_quantity": "qty"})

            if not inv_frame.limit(1).collect().is_empty():
                on_hand_df = (
                    inv_frame.filter(pl.col("subinventory").is_in(["FG", "Ecom"]))
                    .with_columns(
                        pl.lit("ON_HAND").alias("ctn"),
                        # Assign a very early ETA to ensure it sorts first
                        pl.lit(datetime.today()).alias("eta"),
                        pl.lit(-1).alias(
                            "batch_order"
                        ),  # Lowest order to guarantee first slot
                    )
                    .select(["cap_name", "ctn", "eta", "qty", "batch_order"])
                )
                supply_dfs.append(on_hand_df)

        # --- 2.2 Process Future Inventory (STOCK) ---
        if stock is not None:
            # 2.2a. Flatten Batch Map (Container ID -> ETA)
            batch_map: Dict[str, Dict[str, Any]] = stock.get("batch")
            stock_schema: StockPlanSchema = stock.get("schema")

            batch_data = []
            for ctn_id, dates in batch_map.items():
                batch_data.append(
                    {
                        "ctn": ctn_id,
                        "eta": dates.get("inventory_date"),
                    }
                )

            batch_df = (
                pl.DataFrame(batch_data)
                .sort("eta")
                .with_columns(
                    pl.col("eta")
                    .rank(method="ordinal")
                    .cast(pl.Int32)
                    .alias("batch_order")
                )
                .lazy()
            )

            # 2.2b. Melt Stock DF (Wide to Long) and Join with Batch Dates
            ctn_cols = stock_schema.shipping_cols
            id_cols = stock_schema.id_cols

            _stock_frame: pl.LazyFrame = stock.frame.select(id_cols + ctn_cols)

            melted_stock = _stock_frame.unpivot(
                index=id_cols,
                on=ctn_cols,
                variable_name="ctn",
                value_name="qty",
            ).filter(pl.col("qty") > 0)

            future_inv_df = (
                melted_stock.join(
                    batch_df.select(["ctn", "eta", "batch_order"]), on="ctn", how="left"
                )
                .filter(pl.col("eta").is_not_null())
                .select(["cap_name", "ctn", "eta", "qty", "batch_order"])
            )

            supply_dfs.append(future_inv_df)

        # --- 2.3 Combine All Supply and Calculate Final Cumulative Quantity ---
        if supply_dfs:
            inv_by_ctn = pl.concat(supply_dfs)

            # Sort chronologically by ETA, then by batch_order for tie-breaking
            inv_by_ctn = inv_by_ctn.sort(["cap_name", "eta", "batch_order"])

            inv_by_ctn = inv_by_ctn.with_columns(
                # The final cumulative supply curve
                cumulative_qty=pl.col("qty").cum_sum().over("cap_name")
            ).select(
                pl.col("cap_name"),
                pl.col("ctn"),
                pl.col("eta"),
                pl.col("cumulative_qty"),
            )

            # --- 3. Perform Asof Join Allocation ---
            if not inv_by_ctn.limit(1).collect().is_empty():
                out = out.join_asof(
                    inv_by_ctn,
                    by="cap_name",
                    left_on="accumulated_bo_qty",
                    right_on="cumulative_qty",
                    # Strategy "forward" ensures fulfillment (Supply >= Demand)
                    strategy="forward",
                )
            else:
                out = out.with_columns(
                    pl.lit(None).alias("eta"), pl.lit(None).alias("ctn")
                )
        else:
            # If neither INV nor STOCK provided, all backorders have no ETA
            out = out.with_columns(pl.lit(None).alias("eta"), pl.lit(None).alias("ctn"))
        return out

    def process(
        self,
        lr: LoadResult | None,
        stock=None | LoadResult,
        inv=None | LoadResult,
    ) -> LoadResult | None:
        schema = self.schema_cls()

        if lr is None:
            return None

        out = (
            lr.frame.with_columns(
                (pl.col("Item Model").fill_null("Item NO."))
                .str.to_uppercase()
                .alias("Item Model"),
                pl.col("PO NO.").alias("PO Number"),
            )
            .with_columns(
                pl.col("Order Date").dt.strftime("%Y-%m").alias("Year-month"),
                cap_name=self.clean_cap_name("Item Model"),
            )
            .with_columns(
                CLT=self.build_client_code("Customer"),
                cap_cust=self.clean_company_name("Customer"),
            )
            .sort(["Item Model", "SO NO."])
            .with_columns(
                waitlist_order=pl.col("SO NO.").rank(method="ordinal").over("cap_name"),
                accumulated_bo_qty=pl.when(pl.col("Remain Qty") > 0)
                .then(pl.col("Remain Qty"))
                .otherwise(0)
                .cum_sum()
                .over("cap_name"),
            )
            .rename(self.clean_col_name)
            .rename({"onhand_qty": "on_hand_quantity"})
        )

        if inv is not None and stock is not None:
            out = self.calculate_bo_fulfilment(out, inv, stock)

        cap_name_pair = out.select(["item_model", "cap_name"]).unique()
        cap_cust_pair = out.select(["customer", "cap_cust"]).unique()

        out = out.select(schema.all_cols)
        lr.add(schema=schema, cap_name_pair=cap_name_pair, cap_cust_pair=cap_cust_pair)

        return LoadResult(frame=out, context=lr.context)

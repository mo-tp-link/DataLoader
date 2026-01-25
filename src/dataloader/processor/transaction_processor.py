import polars as pl
from datetime import timedelta, date

from dataloader.extractions.inventory_loader import InventoryLoader
from dataloader.processor.inventory_processor import InvProcessor
from dataloader.schemas.transaction_schema import TransactionSchema
from dataloader.utils import LoadResult
from .abstract_processor import ProcessorAbstract


class TransProcessor(ProcessorAbstract):
    schema_cls = TransactionSchema

    def load_starting_inv(self) -> pl.LazyFrame:
        lr = InventoryLoader().load("./data/Inventory_Information_Starting.xlsx")
        out = InvProcessor().convert_to_transaction(lr)
        return out

    def build_future(self, trans: LoadResult, stock: LoadResult) -> pl.LazyFrame:
        batch = stock.context.get("batch")
        schedule = stock.context.get("schedule")
        stage_arrivals = {
            stage.stage: (
                date.today() + timedelta(days=stage.inventory_offset_days)
            ).isoformat()
            for stage in schedule
        }
        schema = stock.get("schema")

        in_transit_cols = schema.shipping_cols
        schedule_cols = schema.schedule_cols
        id_cols = ["item_model"]

        variable_name = "Order No."
        qty_nam = "Quantity"

        tommorow = date.today() + timedelta(days=1)
        in_transit = (
            stock.frame.select(id_cols + in_transit_cols)
            .unpivot(
                on=in_transit_cols,
                index=id_cols,
                variable_name=variable_name,
                value_name=qty_nam,
            )
            .with_columns(
                pl.col(variable_name)
                .replace(
                    {
                        k: v["inventory_date"].date()
                        if v["inventory_date"].date() > date.today()
                        else tommorow
                        for k, v in batch.items()
                    }
                )
                .str.strptime(pl.Date, "%Y-%m-%d")
                .alias("Date"),
                pl.col(variable_name).alias("Customer"),
            )
        )

        in_production = (
            stock.frame.select(id_cols + schedule_cols)
            .unpivot(
                on=schedule_cols,
                index=id_cols,
                variable_name=variable_name,
                value_name=qty_nam,
            )
            .with_columns(
                pl.col(variable_name)
                .replace(stage_arrivals)
                .str.strptime(pl.Date, "%Y-%m-%d")
                .alias("Date"),
                pl.col(variable_name).alias("Customer"),
            )
        )

        stock_in_trans_format = (
            pl.concat(
                [in_transit, in_production],
                how="diagonal",
            )
            .with_columns(
                pl.lit("Future Order").alias("Source Type"),
                pl.lit("FG").alias("Subinventory"),
                # pl.lit("TP-CN").alias("Customer"),
                pl.lit("Mo").alias("Created By"),
            )
            .filter(pl.col(qty_nam) != 0)
            .rename({"item_model": "Item Model"})
        )
        return stock_in_trans_format

    def process(
        self,
        lr: LoadResult,
        include_past=True,
        stock=None | LoadResult,
        *args,
        **kwargs,
    ):
        schema = self.schema_cls()
        lf = lr.frame.with_columns(
            pl.col("Order Date").str.strptime(pl.Date, "%d-%b-%Y", strict=True),
        )

        if include_past:
            init_inv = self.load_starting_inv()
            lf = pl.concat([init_inv, lf], how="align")

        if stock is not None:
            future = self.build_future(lr, stock)
            lf = pl.concat([future, lf], how="align")
        out = (
            lf.with_columns(
                (pl.col("Item Model").fill_null(pl.col("Item Number")))
                .str.to_uppercase()
                .alias("Item Model"),
                pl.col("Order Date").dt.strftime("%Y-%m").alias("Year-month"),
                pl.when(
                    (pl.col("Source Type") == "Purchase order")
                    & (pl.col("Customer").is_null())
                )
                .then(pl.lit("TP-CN"))
                .otherwise("Customer")
                .alias("Customer"),
            )
            .with_columns(
                cap_name=self.clean_cap_name("Item Model"),
                CLT=self.build_client_code("Customer"),
                cap_cust=self.clean_company_name("Customer"),
            )
            .rename(self.clean_col_name)
        )

        cap_name_pair = out.select(["item_model", "cap_name"])
        cap_cust_pair = out.select(["customer", "cap_cust"])
        out = out.select(schema.all_cols)
        lr.add(schema=schema, cap_name_pair=cap_name_pair, cap_cust_pair=cap_cust_pair)
        return LoadResult(frame=out, context=lr.context)

import polars as pl

from dataloader.schemas.inventory_info_schema import InventorySchema
from dataloader.utils import LoadResult
from .abstract_processor import ProcessorAbstract


class InvProcessor(ProcessorAbstract):
    schema_cls = InventorySchema

    def convert_to_transaction(
        self, lr: LoadResult, year: int = 2024, month: int = 11, day: int = 28
    ) -> pl.LazyFrame:
        """2024,11,28 is earist transaction data I had. so I used it as begin status"""
        # WARNING: This date matches InventoryInformation_start's dates
        need_to_change_name = {
            "Inventory Organization": "Orgnization",
            # "Customer Name": "Customer", # This is Blank, so no need to include
            "On-hand quantity": "Quantity",
        }

        exactly_same = [
            "Item Number",
            "Item Model",
            "Item Spec",
            "Item Version",
            "Country Code",
            "Customer Class",
            "Subinventory",
        ]
        # import  streamlit as st
        # st.write(lr.frame)

        return lr.frame.select(
            pl.col(exactly_same),
            pl.col(need_to_change_name.keys()),
            pl.date(year, month, day).alias("Date"),
            pl.lit("Purchase Order").alias("Source Type"),
            pl.lit("Initial Inventory").alias("Customer"),
        ).rename(need_to_change_name)

    def process(self, lr: LoadResult) -> LoadResult:
        schema = self.schema_cls()

        out = (
            lr.frame.with_columns(
                (pl.col("Item Model").fill_null(pl.col("Item Number")))
                .str.to_uppercase()
                .alias("Item Model"),
                pl.col("Subinventory").fill_null(pl.col("Customer Name")),
            )
            .with_columns(
                cap_name=self.clean_cap_name("Item Model"),
            )
            .rename(self.clean_col_name)
        )
        cap_name_pair = out.select(["item_model", "cap_name"]).unique()
        lr.add(schema=schema, cap_name_pair=cap_name_pair)
        out = out.select(schema.all_cols)
        return LoadResult(frame=out, context=lr.context)

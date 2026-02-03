import polars as pl

from dataloader.schemas import POSSchema
from dataloader.utils import LoadResult
from .abstract_processor import ProcessorAbstract


def assign_team_colors(df: pl.LazyFrame, col: str) -> dict[str, str]:
    """TODO: Implement team color assignment logic."""
    return {}


class POSProcessor(ProcessorAbstract):
    schema_cls = POSSchema
    MAJOR_PARTENERS = [  # From POS dirictly
        "AMAZON",
        "BEST BUY CANADA LTD",
        "Canada Computers",
        "COSTCO",
        "MEMORY EXPRESS",
        "STAPLES CANADA ULC",
        "WAL-MART CANADA CORP",
        "TELUS COMMUNICATIONS INC",
    ]
    # GNR
    CLT_MAP = {
        "AMAZON": "AMZ",
        "BEST BUY CANADA LTD": "BBY",
        "CANADA COMPUTERS": "CCT",
        "STAPLES CANADA ULC": "STP",
        "WAL-MART CANADA CORP": "WMT",
        "TELUS COMMUNICATIONS INC": "TLS",
    }

    def process(self, lr: LoadResult | None, **kwargs) -> LoadResult | None:
        schema = self.schema_cls()
        # Only add to lr when shcnema has confimred

        if lr.frame.limit(1).collect().is_empty():
            print("No POS Loaded")
            return lr

        change_to_upper_case = ["Sales Team", "Business Segment", "Disti"]

        out = (
            lr.frame.with_columns(
                *(self.clean_cat_str(c) for c in change_to_upper_case),
                pl.col("Item Model").str.to_uppercase(),
                cap_cust=self.clean_company_name("Reseller"),
                focused_partner=pl.when(pl.col("Reseller").is_in(self.MAJOR_PARTENERS))
                .then("Reseller")
                .otherwise("Sales Team"),
            )
            .with_columns(
                pl.col("focused_partner").str.to_uppercase(),
                cap_name=self.clean_cap_name("Item Model"),
            )
            .with_columns(
                clt=pl.col("focused_partner").replace_strict(
                    self.CLT_MAP, default="GNR"
                )
            )
            .rename(
                {
                    # "MFG#": "Item Model",
                    "Reseller": "Reseller Name",
                    "Disti": "Distributor",
                    "Qty": "Quantity",
                }
            )
            .rename(self.clean_col_name)
        )
        cap_name_pair = out.select(["item_model", "cap_name"]).unique()
        cap_cust_pair = out.select(["reseller_name", "cap_cust"]).unique()

        team_color = assign_team_colors(out, "focused_partner")
        lr.add(
            schema=schema,
            cap_name_pair=cap_name_pair,
            cap_cust_pair=cap_cust_pair,
            team_color=team_color,
        )

        out = out.select(schema.all_cols)
        return LoadResult(frame=out, context=lr.context)

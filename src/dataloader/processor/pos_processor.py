import polars as pl

from dataloader.schemas import POSSchema
from dataloader.utils import LoadResult

from .abstract_processor import ProcessorAbstract


def assign_team_colors(df: pl.LazyFrame, col: str) -> dict[str, str]:
    """TODO: Implement team color assignment logic."""
    return {}


class POSProcessor(ProcessorAbstract):
    schema_cls = POSSchema
    MAJOR_PARTENERS = [  # From POS dirictly  # noqa: RUF012
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
    CLT_MAP = {  # noqa: RUF012
        "AMAZON": "AMZ",
        "BEST BUY CANADA LTD": "BBY",
        "CANADA COMPUTERS": "CCT",
        "STAPLES CANADA ULC": "STP",
        "WAL-MART CANADA CORP": "WMT",
        "TELUS COMMUNICATIONS INC": "TLS",
    }
    CRM_DISTI_NAME = {  # noqa: RUF012
        "LONGTECH": "LONGTECH COMPUTER DISTRIBUTION INC",
        "ADI": "Ademco III Ltd.",
        "NSI": "NSI DISTRIBUTION / 2164929 ONTARIO INC",
        "TDL": "TDL CANADA INC.",
        "ASI": "ASI Computer Technologies (Canada) Corp",
        "DH": "D & H Canada ULC",
        "AMETA": "Ameta International Co. Ltd.",
        "ANIXTER": "Anixter Canada Inc.",
        "INGRAM": "Ingram Micro LP",
        "RS": "RS DISTRIBUTION INC.",
        "SYNNEX": "TD SYNNEX Canada ULC",
        "LUMAN": "LUMEN / SONECABLE Division of Sonepar Canada Inc.",
        "DOUBLE RADIUS": "DoubleRadius, Inc.",
        "RANDMAR": "RANDMAR INC.",
        "TARGO COMMUNICATIONS INC": "Targo Communications Inc.",
        "TELUS COMMUNICATIONS INC": "TELUS Communications Inc.",
        "MBSI": "MBSI WAV LP",
        "LUMEN - SONEPAR CANADA INC": "Sonepar Canada Inc.",
        "BESTBUY": "Best Buy Canada Ltd",
    }

    def process(self, lr: LoadResult | None, **kwargs) -> LoadResult | None:
        schema = self.schema_cls()
        # Only add to lr when shcnema has confimred

        assert lr is not None
        _first = lr.frame.limit(1).collect()
        assert isinstance(_first, pl.DataFrame)

        if _first.is_empty():
            print("No POS Loaded")
            return lr

        change_to_cap_name = [
            "Disti",
            # "Business Segment",
        ]
        change_to_upper_case = ["Reseller", "Item Model"]

        out = (
            lr.frame.with_columns(
                *(self.clean_cat_str(c) for c in change_to_cap_name),
                *(pl.col(c).str.to_uppercase() for c in change_to_upper_case),
                cap_cust=self.clean_company_name("Reseller"),
            )
            .with_columns(
                focused_partner=pl.when(pl.col("Reseller").is_in(self.MAJOR_PARTENERS))
                .then("Reseller")
                .otherwise("Sales Team"),
            )
            .with_columns(
                pl.col("focused_partner").str.to_uppercase(),
                base_mfg=pl.col("Item Model").str.replace(r"_(RE|OV|OPENBOX|CACIK|CAXP|CADTL)$", ""),
            )
            .with_columns(
                clt=pl.col("focused_partner").replace_strict(self.CLT_MAP, default="GNR"),
                # clt=pl.col("focused_partner"),
                cap_name=self.clean_cap_name("base_mfg"),
            )
            # .with_columns(crm_disti_name=pl.col("Disti").replace(self.CRM_DISTI_NAME))
            .rename(
                {
                    # "MFG#": "Item Model",
                    "Reseller": "Reseller Name",
                    "Disti": "Distributor",
                    "Qty": "Quantity",
                }
            )
            .rename(self.clean_col_name)
            .with_columns(pl.col("sales_team").str.to_uppercase().alias("sales_team"))
        )
        cap_name_pair = out.select(["item_model", "cap_name"]).unique()
        cap_cust_pair = out.select(["reseller_name", "cap_cust"]).unique()

        team_color = assign_team_colors(out, "focused_partner")
        lr.add(
            schema=schema,
            cap_name_pair=cap_name_pair,
            cap_cust_pair=cap_cust_pair,
            team_color=team_color,
            _full_path=kwargs.get("search_dir", ""),
        )

        out = out.select(schema.all_cols)
        return LoadResult(frame=out, context=lr.context)

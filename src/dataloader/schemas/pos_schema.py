from dataclasses import dataclass, field


@dataclass
class POSSchema:
    # WARNING: Cols below might have duplicates
    id_cols: list[str] = field(default_factory=lambda: ["cap_name", "cap_cust"])
    product_cols: list[str] = field(
        default_factory=lambda: ["item_model", "bu", "category", "sub_category"]
    )
    transaction_cols: list[str] = field(
        default_factory=lambda: [
            "invoice",
            "distributor",
            "invoice_date",
        ]
    )
    customer_cols: list[str] = field(
        default_factory=lambda: [
            "reseller_name",
            "province",
            "region",
            "zip_code",
            "vir_exclusion",
            "buy_in_group",
            "focused_partner",
            "clt"
        ]
    )
    sales_cols: list[str] = field(
        default_factory=lambda: ["account_manager", "business_segment", "sales_team"]
    )
    qty_cols: list[str] = field(default_factory=lambda: ["quantity"])
    price_cols: list[str] = field(default_factory=lambda: ["price", "amount"])
    date_cols: list[str] = field(
        default_factory=lambda: [
            "created_time",
            "year_month",
            "year",
            "month",
            "invoice_week",
        ]
    )

    @property
    def all_cols(self) -> set[str]:
        """Return all known columns in the schema."""
        return set(
            self.id_cols
            + self.product_cols
            + self.transaction_cols
            + self.customer_cols
            + self.sales_cols
            + self.qty_cols
            + self.price_cols
            + self.date_cols
        )

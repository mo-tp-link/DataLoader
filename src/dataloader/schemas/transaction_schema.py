from dataclasses import dataclass, field


@dataclass
class TransactionSchema:
    id_cols: list[str] = field(
        default_factory=lambda: ["cap_name", "cap_cust", "subinventory"]
    )
    trans_cols: list[str] = field(
        default_factory=lambda: [
            "source_type",
            "order_no",
            # "ci_stampno",
            "transfer_subinventory",
            "transaction_type",
            "remark",
            # "orgnization",
            # "destination_org",
            # "pi_number",
            # "HS CODE",
            # "GREEN Tax ",
            # "GT Category",
        ]
    )
    customer_cols: list[str] = field(
        default_factory=lambda: [
            "po_number",
            "created_by",
            "customer",
            "clt",
        ]
    )
    item_cols: list[str] = field(
        default_factory=lambda: [
            # "item_number",
            "item_model",
            "item_spec",
            "item_version",
            "customer_class",
            "country_code",
            # "reference_version",
            # "bu",
        ]
    )
    qty_cols: list[str] = field(
        default_factory=lambda: [
            "quantity",
        ]
    )
    date_cols: list[str] = field(
        default_factory=lambda: ["date", "order_date", "year_month"]
    )

    @property
    def all_cols(self) -> set[str]:
        """Return all known columns in the schema."""
        return set(
            self.id_cols
            + self.trans_cols
            + self.customer_cols
            + self.item_cols
            + self.qty_cols
            + self.date_cols
        )

    # TODO: Need finish implementation

from dataclasses import dataclass, field


@dataclass
class BackOrderSchema:
    id_cols: list[str] = field(
        default_factory=lambda: ["cap_name", "subinventory", "cap_cust"]
    )

    customer_cols: list[str] = field(
        default_factory=lambda: [
            "po_number",
            "so_no",
            "creator",
            # "currency",
            "customer",
            "clt",
        ]
    )

    item_cols: list[str] = field(
        default_factory=lambda: [
            # "item_no",
            "item_model",
            "item_spec",
            # "item_version",
            "waitlist_order",
            "ctn",
            'eta'

        ]
    )

    qty_cols: list[str] = field(
        default_factory=lambda: [
            "order_qty",
            "shipped_qty",
            "received_qty",
            "reserved_qty",
            "remain_qty",
            "on_hand_quantity",
            "available_qty",
            # "accumulated_bo_qty",
        ]
    )

    amount_cols: list[str] = field(
        default_factory=lambda: [
            # "price",
            # "amount",
            # "bo_amount",
            # "bo_amount_sales_tax",
            # "order_amount_sales_tax",
        ]
    )
    dates_cols: list[str] = field(
        default_factory=lambda: [
            "order_date",
            "request_date",
            "schedule_ship_date",
            "latest_eta",
            "year_month",
        ]
    )

    @property
    def all_cols(self) -> set[str]:
        """Return all known columns in the schema."""
        return set(
            self.id_cols
            + self.customer_cols
            + self.item_cols
            + self.qty_cols
            + self.amount_cols
            + self.dates_cols
        )

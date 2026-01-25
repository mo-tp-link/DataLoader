from dataclasses import dataclass, field


@dataclass
class InventorySchema:
    id_cols: list[str] = field(default_factory=lambda: ["cap_name", "subinventory"])

    item_cols: list[str] = field(
        default_factory=lambda: [
            # "item_number",
            "item_model",
            "item_spec",
            # "item_version",
            # "description",
            # "country_code",
            # "customer_class",
            # "business_unit",
            # "power_spec",
            # "subcategory",
            # "ean_13",
            # "upc_12",
            # "item_description",
            # "subinventory",
        ]
    )

    qty_cols: list[str] = field(
        default_factory=lambda: [
            "on_hand_quantity",
            "available_quantity",
            "reservation_quantity",
            "in_transit_quantity",
            "bo_quantity",
        ]
    )
    other_cols: list[str] = field(
        default_factory=lambda: [
            "on_hand_day",
        ]
    )
    @property
    def all_cols(self) -> set[str]:
        """Return all known columns in the schema."""
        return set(
            self.id_cols
            + self.item_cols
            + self.qty_cols
            + self.other_cols
        )

    def __post_init__(self):
        pass

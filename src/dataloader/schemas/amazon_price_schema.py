from dataclasses import dataclass, field


@dataclass
class AMZPriceSchema:
    # WARNING: Cols below might have duplicates
    id_cols: list[str] = field(default_factory=lambda: ["cap_name"])

    product_cols: list[str] = field(default_factory=lambda: ["item_model", "asin"])
    price_cols: list[str] = field(default_factory=lambda: ["value"])
    timestamp_cols: list[str] = field(default_factory=lambda: ["timestamp"])

    @property
    def all_cols(self) -> set[str]:
        """Return all known columns in the schema."""
        return set(
            self.id_cols + self.price_cols + self.product_cols + self.timestamp_cols
        )

from dataclasses import dataclass, field


@dataclass
class PriceSchema:
    # WARNING: Cols below might have duplicates
    id_cols: list[str] = field(default_factory=lambda: ["cap_name"])

    product_cols: list[str] = field(
        default_factory=lambda: ["item_model", "short_product_description"]
    )
    price_cols: list[str] = field(
        default_factory=lambda: [
            "disty_cost_cad",
            "vad_cost_cad",
            "tdl_cost_cad",
            "kgp_cost_cad",
            "ameta_cost_cad",
        ]
    )

    @property
    def all_cols(self) -> set[str]:
        """Return all known columns in the schema."""
        return set(self.id_cols + self.price_cols + self.product_cols)

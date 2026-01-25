from dataclasses import dataclass, field

# [
#     "rebate_type",
#     "status",
#     "content_sha",
#     "creation_date",
#     "year_month",
#     "cap_name",
#     "cap_cust",
# ]
#


@dataclass
class SPASchema:
    # WARNING: Cols below might have duplicates
    deal_cols: list[str] = field(
        default_factory=lambda: [
            "spa",
            "deal_size",
            "deal_description",
        ]
    )
    applicant_cols: list[str] = field(
        default_factory=lambda: [
            "applicant",
            "applicant_email",
            "application_cc",
        ]
    )
    disty_cols: list[str] = field(
        default_factory=lambda: [
            "distributor",
            "distributor_rep_email",
        ]
    )
    approve_cols: list[str] = field(
        default_factory=lambda: [
            "next_approver",
            "approved_by",
            "approved_date",
            "approved_notes",
        ]
    )
    qty_cols: list[str] = field(
        default_factory=lambda: [
            "minimum_quantity",
            "maximum_quantity",
            "expected_quantity",
        ]
    )
    end_user_cols: list[str] = field(
        default_factory=lambda: [
            "end_user",
            "end_user_email",
            "end_user_vertical",
        ]
    )
    reseller_cols: list[str] = field(
        default_factory=lambda: [
            "reseller_name",
            "reseller_rep_email",
        ]
    )
    duration_cols: list[str] = field(
        default_factory=lambda: ["expiration_date", "effective_date"]
    )

    id_cols: list[str] = field(
        default_factory=lambda: [
            "cap_name",
            "cap_cust",
            "expiration_date",
            "distributor",
            "end_user",
            "item_model",
            "reseller_name",
        ]
    )
    price_cols: list[str] = field(
        default_factory=lambda: [
            "list_price",
            "discount_percentage",
            "discount_amount",
            "pre_load_discount",
            "total_discount",
            "total_discount_pctg",
            "net_cost",
        ]
    )

    @property
    def all_cols(self) -> set[str]:
        """Return all known columns in the schema."""
        return set(
            self.id_cols
            + self.deal_cols
            + self.applicant_cols
            + self.disty_cols
            + self.approve_cols
            + self.qty_cols
            + self.end_user_cols
            + self.reseller_cols
            + self.duration_cols
            + self.price_cols
        )

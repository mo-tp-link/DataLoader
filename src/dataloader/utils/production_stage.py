from dataclasses import dataclass
from .variables import HQ_BO_WAIT_TIME, MANUFCATURE_TIME, SHIPPING_TIME
from datetime import datetime


@dataclass
class ProductionStageSchedule:
    stage: str
    ship_offset_days: int  # days from the snapshot until the container leaves
    transit_days: int  # sailing time
    receiving_buffer_days: int = 0  # optional customs/receiving slack

    @property
    def inventory_offset_days(self) -> int:
        return self.ship_offset_days + self.transit_days + self.receiving_buffer_days


production_stage_schedule = [
    ProductionStageSchedule(
        stage="waiting_for_delivery",
        ship_offset_days=7,  # almost ready, expect to load in a week
        transit_days=SHIPPING_TIME,
    ),
    ProductionStageSchedule(
        stage="not_ready_for_delivery",
        ship_offset_days=MANUFCATURE_TIME,
        transit_days=SHIPPING_TIME,
    ),
    ProductionStageSchedule(
        stage="hq_bo",
        ship_offset_days=MANUFCATURE_TIME + HQ_BO_WAIT_TIME,
        transit_days=SHIPPING_TIME,
    ),
]


@dataclass
class InventoryStatus:
    hq_bo_time = 30
    manufacturing_time = 15
    shipping_time = 38
    lead_time = manufacturing_time + shipping_time

    in_inv_week = 4
    in_transit_week = (shipping_time // 7) + (
        (shipping_time % 7) > 3
    )  # Round up to whole week
    in_production_week = (manufacturing_time // 7) + (
        (manufacturing_time % 7) > 3
    )  # Round up to whole week
    inv_start_date = datetime(
        year=2024, month=11, day=1
    )  # Dont change unless init_Inv changes

    def __repr__(self) -> str:
        return f"In-Inventory {self.in_inv_week} weeks, In-Transit: {self.in_transit_week} weeks, In-Production: {self.in_production_week} weeks"


inventory_status = InventoryStatus()


@dataclass
class PartnerInventory:
    partner_week: int = 1
    name: str | None = None
    abbr: str = "GNR"
    sub_inv: str = "FG"
    in_inv_week = inventory_status.in_inv_week
    in_transit_week = inventory_status.in_transit_week
    in_production_week = inventory_status.in_production_week


partner_inventories = [
    PartnerInventory(0, None, "GNR", "FG"),
    PartnerInventory(4, "Amazon.com.ca, Inc.", "AMZ", "AMZ"),
    PartnerInventory(6, "Best Buy Canada Ltd", "BBY", "FG"),
    PartnerInventory(1, "Ingram Micro LP", "WMT", "FG"),
    PartnerInventory(1, "STAPLES CANADA ULC", "STP", "FG"),
    PartnerInventory(1, "TELUS Communications Inc.", "TLS", "FG"),
    PartnerInventory(1, "ASI Computer Technologies(Canada) Corp.", "CCT", "FG"),
]

from typing import Type

from dataloader.utils import LoadResult

REGISTRY: dict[str, tuple[Type, Type]] = {}


def register(name: str, loader: Type, processor: Type):
    """Register a (loader, processor) pair under a name."""
    REGISTRY[name] = (loader, processor)


def get_data(name: str, **kwargs) -> LoadResult:
    """Generic getter: load and process data based on registry entry."""
    if name not in REGISTRY:
        raise KeyError(
            f"{name!r} not found in REGISTRY. Registered: {list(REGISTRY.keys())}"
        )

    loader_cls, processor_cls = REGISTRY[name]
    lr = loader_cls().load(**kwargs)
    processor = processor_cls()
    return processor.process(lr, **kwargs)


# --- Register all your data types here ---
def setup_registry():
    from dataloader.extractions import (
        StockLoader,
        BOLoader,
        InventoryLoader,
        POSLoader,
        TransactionLoader,
        SPALoader,
        PriceLoader,
        ForecastLoader,
        AMZPriceLoader,
    )
    from dataloader.processor import (
        StockProcessor,
        BOProcessor,
        InvProcessor,
        POSProcessor,
        TransProcessor,
        SPAProcessor,
        PriceProcessor,
        ForecastProcessor,
        AMZPriceProcessor,
    )

    register("stock", StockLoader, StockProcessor)
    register("bo", BOLoader, BOProcessor)
    register("inv", InventoryLoader, InvProcessor)
    register("pos", POSLoader, POSProcessor)
    register("trans", TransactionLoader, TransProcessor)
    register("spa", SPALoader, SPAProcessor)
    register("price", PriceLoader, PriceProcessor)
    register("forecast", ForecastLoader, ForecastProcessor)
    register("msrp", AMZPriceLoader, AMZPriceProcessor)


# --- Optional shortcut ---
def get_all_data() -> dict[str, object]:
    """Return processed data for all registered sources."""
    return {name: get_data(name) for name in REGISTRY}


# Initialize registry on import
setup_registry()

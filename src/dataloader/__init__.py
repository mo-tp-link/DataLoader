"""
tplink-dataloader: A modular data loading and processing framework.

Usage:
    from dataloader import DataManager, LoadResult

    # With pre-configured sources (TP-Link specific)
    dm = DataManager(data_dir="./data")
    result = dm.get("stock")

    # As a framework (extend with your own loaders/processors)
    from dataloader import DataManager, DataLoaderABC, ProcessorAbstract

    class MyLoader(DataLoaderABC):
        ...

    class MyProcessor(ProcessorAbstract):
        ...

    dm = DataManager(auto_setup=False)
    dm.register("my_data", MyLoader, MyProcessor)
"""

__version__ = "0.1.0"

# Core classes
from .data_manager import DataManager, DataSource
from .utils import (
    LoadResult,
    clean_cap_name,
    clean_col_name,
    clean_company_name,
    clean_cap_name_str,
    tl_map,
)

# Base classes for extension
from .extractions import DataLoaderABC
from .processor import ProcessorAbstract

# Registry utilities
from .registry import REGISTRY, get_all_data, get_data, register

__all__ = [
    # Core
    "DataManager",
    "DataSource",
    "LoadResult",
    # Base classes
    "DataLoaderABC",
    "ProcessorAbstract",
    # Registry
    "REGISTRY",
    "get_data",
    "get_all_data",
    "register",
    "clean_cap_name",
    "clean_col_name",
    "clean_company_name",
    "tl_map",
    # Version
    "__version__",
    "clean_cap_name_str",
]

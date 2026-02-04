"""
DataManager: A centralized data management class that acts as a repository layer.

This class provides:
- Unified access to all registered data sources by name
- Caching with lazy loading for efficient memory usage
- Dependency resolution between data sources
- Easy injection into other classes
"""

from __future__ import annotations

import polars as pl
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from dataloader.utils import LoadResult

# Type alias for registered data source names
DataSourceName = Literal["stock", "bo", "inv", "pos", "trans", "forecast", "msrp"]


@dataclass
class DataSource:
    """Metadata container for a registered data source."""

    name: str
    loader_cls: type
    processor_cls: type
    dependencies: list[str] = field(default_factory=list)


class DataManager:
    """
    Centralized data management class providing repository-pattern access to all data sources.

    Usage:
        # Initialize with data directory
        manager = DataManager(data_dir="./data")

        # Load data by name (lazy-loaded and cached)
        stock_result = manager.get("stock")
        bo_result = manager.get("bo")

        # Access the DataFrame
        df = manager.get("stock").frame.collect()

        # Access with dependencies auto-resolved
        trans_result = manager.get("trans")  # automatically loads stock if needed

        # Refresh specific data
        manager.invalidate("stock")
        fresh_stock = manager.get("stock")

        # Refresh all data
        manager.invalidate_all()

        # Inject into another class
        class MyAnalyzer:
            def __init__(self, data_manager: DataManager):
                self.dm = data_manager

            def analyze(self):
                stock = self.dm.get("stock")
                ...
    """

    _sources: dict[str, DataSource]
    _cache: dict[str, "LoadResult"]
    _data_dir: Path
    _overrides: dict[str, dict[str, Any]]

    def __init__(
        self,
        data_dir: str | Path = "./data",
        auto_setup: bool = True,
    ) -> None:
        """
        Initialize the DataManager.

        Args:
            data_dir: Base directory for data files.
            auto_setup: If True, automatically register all known data sources.
        """
        self._sources = {}
        self._cache = {}
        self._data_dir = Path(data_dir)
        self._overrides = {}

        if auto_setup:
            self._setup_sources()

    def _setup_sources(self) -> None:
        """Register all known data sources with their dependencies."""
        from dataloader.extractions import (
            AMZPriceLoader,
            BOLoader,
            ForecastLoader,
            InventoryLoader,
            POSLoader,
            # PriceLoader,
            # SPALoader,
            StockLoader,
            TransactionLoader,
        )
        from dataloader.processor import (
            AMZPriceProcessor,
            BOProcessor,
            ForecastProcessor,
            InvProcessor,
            POSProcessor,
            # PriceProcessor,
            # SPAProcessor,
            StockProcessor,
            TransProcessor,
        )

        # Register sources with their dependencies
        self.register("stock", StockLoader, StockProcessor)
        self.register("bo", BOLoader, BOProcessor, dependencies=["inv", "stock"])
        self.register("inv", InventoryLoader, InvProcessor)
        self.register("pos", POSLoader, POSProcessor)
        self.register(
            "trans", TransactionLoader, TransProcessor, dependencies=["stock"]
        )
        # self.register("spa", SPALoader, SPAProcessor)
        # self.register("price", PriceLoader, PriceProcessor)
        self.register("forecast", ForecastLoader, ForecastProcessor)
        self.register("msrp", AMZPriceLoader, AMZPriceProcessor)

    def register(
        self,
        name: str,
        loader_cls: type,
        processor_cls: type,
        dependencies: list[str] | None = None,
    ) -> None:
        """
        Register a data source.

        Args:
            name: Unique identifier for the data source.
            loader_cls: The loader class (subclass of DataLoaderABC).
            processor_cls: The processor class (subclass of ProcessorAbstract).
            dependencies: List of other data source names this source depends on.
        """
        self._sources[name] = DataSource(
            name=name,
            loader_cls=loader_cls,
            processor_cls=processor_cls,
            dependencies=dependencies or [],
        )

    def configure(self, name: str, **kwargs: Any) -> "DataManager":
        """
        Configure loading parameters for a data source.

        Args:
            name: The data source name.
            **kwargs: Parameters to pass to the loader/processor.

        Returns:
            Self for method chaining.

        Example:
            manager.configure("stock", path="custom_stock.csv").get("stock")
        """
        if name not in self._sources:
            raise KeyError(
                f"Unknown data source: {name!r}. Available: {self.available}"
            )
        self._overrides[name] = kwargs
        return self

    def get(
        self,
        name: DataSourceName | str,
        *,
        refresh: bool = False,
        **kwargs: Any,
    ) -> "LoadResult":
        """
        Get processed data by name.

        Args:
            name: The data source identifier.
            refresh: If True, force reload even if cached.
            **kwargs: Override parameters for this specific load.

        Returns:
            LoadResult containing the processed LazyFrame and context.

        Raises:
            KeyError: If the data source is not registered.
        """
        if name not in self._sources:
            raise KeyError(
                f"Unknown data source: {name!r}. Available: {self.available}"
            )

        # Return cached if available and not forcing refresh
        if not refresh and name in self._cache and not kwargs:
            return self._cache[name]

        # Load dependencies first
        source = self._sources[name]
        dep_results = {}
        for dep_name in source.dependencies:
            dep_results[dep_name] = self.get(dep_name)

        # Merge overrides with inline kwargs (inline takes precedence)
        merged_kwargs = {**self._overrides.get(name, {}), **kwargs, **dep_results}

        # Load and process
        result = self._load_and_process(source, **merged_kwargs)

        # Cache if no override kwargs
        if not kwargs:
            self._cache[name] = result

        return result

    def _load_and_process(self, source: DataSource, **kwargs: Any) -> "LoadResult":
        """Internal method to load and process a data source."""
        loader = source.loader_cls()
        processor = source.processor_cls()

        lr = loader.load(**kwargs)
        return processor.process(lr, **kwargs)

    def __getitem__(self, name: str) -> "LoadResult":
        """Allow dict-like access: manager['stock']."""
        return self.get(name)

    def __getattr__(self, name: str) -> "LoadResult":
        """
        Allow attribute access: manager.stock.

        Note: Only works for registered data source names.
        """
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")
        if name in self._sources:
            return self.get(name)
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")

    def __contains__(self, name: str) -> bool:
        """Check if a data source is registered: 'stock' in manager."""
        return name in self._sources

    def invalidate(self, name: str) -> None:
        """
        Invalidate cached data for a specific source.

        This also invalidates any sources that depend on the given source.

        Args:
            name: The data source to invalidate.
        """
        if name in self._cache:
            del self._cache[name]

        # Cascade invalidation to dependents
        for source_name, source in self._sources.items():
            if name in source.dependencies and source_name in self._cache:
                del self._cache[source_name]

    def invalidate_all(self) -> None:
        """Clear all cached data."""
        self._cache.clear()

    def preload(self, *names: str) -> "DataManager":
        """
        Eagerly load specified data sources into cache.

        Args:
            *names: Data source names to preload. If empty, preloads all.

        Returns:
            Self for method chaining.
        """
        targets = names if names else self._sources.keys()
        for name in targets:
            self.get(name)
        return self

    def collect(self, name: str, **kwargs: Any) -> pl.DataFrame:
        """
        Convenience method to get collected DataFrame directly.

        Args:
            name: The data source name.
            **kwargs: Override parameters.

        Returns:
            Collected Polars DataFrame.
        """
        return self.get(name, **kwargs).frame.collect()

    def schema(self, name: str) -> Any:
        """
        Get the schema object for a data source.

        Args:
            name: The data source name.

        Returns:
            The schema object from the LoadResult context.
        """
        return self.get(name).get("schema")

    @property
    def available(self) -> list[str]:
        """List all registered data source names."""
        return list(self._sources.keys())

    @property
    def cached(self) -> list[str]:
        """List currently cached data source names."""
        return list(self._cache.keys())

    def status(self) -> dict[str, dict[str, Any]]:
        """
        Get status information for all data sources.

        Returns:
            Dict with source names as keys and status info as values.
        """
        return {
            name: {
                "cached": name in self._cache,
                "dependencies": source.dependencies,
                "loader": source.loader_cls.__name__,
                "processor": source.processor_cls.__name__,
            }
            for name, source in self._sources.items()
        }

    def __repr__(self) -> str:
        cached_count = len(self._cache)
        total_count = len(self._sources)
        return f"DataManager(sources={total_count}, cached={cached_count}, data_dir={self._data_dir})"

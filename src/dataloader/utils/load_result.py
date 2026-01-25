import polars as pl
from typing import Any
from dataclasses import dataclass

@dataclass
class LoadResult:
    frame: pl.LazyFrame
    context: dict[str, Any] | None = None

    def add(self, **kwargs):
        """Add arbitrary metadata."""
        if self.context is None:
            self.context = {}
        self.context.update(kwargs)
        return self

    def get(self, key: str, default=None):
        if self.context is None:
            self.context = {}
        return self.context.get(key, default)


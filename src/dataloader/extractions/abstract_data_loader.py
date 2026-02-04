from __future__ import annotations
import polars as pl
from abc import ABC
from pathlib import Path
from typing import IO

from dataloader.utils import LoadResult


class DataLoaderABC(ABC):
    """Abstract base for all data loaders."""

    data_path: Path = Path("./data")
    header_row = 0
    sheet_name: str | None = None
    str_cols: list[str] | None = None
    int_cols: list[str] | None = None
    float_cols: list[str] | None = None
    date_cols: list[str] | None = None
    datetime_cols: list[str] | None = None
    timestamp_cols: list[str] | None = None
    file_name: str | None = None

    def build_schema(self) -> dict[str, pl.DataType]:
        schema: dict[str, pl.DataType] = {}
        if self.str_cols:
            schema |= {c: pl.String for c in self.str_cols}
        if self.int_cols:
            schema |= {c: pl.Int64 for c in self.int_cols}
        if self.float_cols:
            schema |= {c: pl.Float64 for c in self.float_cols}
        if self.date_cols:
            schema |= {c: pl.Date for c in self.date_cols}
        if self.datetime_cols:
            schema |= {c: pl.Datetime for c in self.datetime_cols}
        if self.timestamp_cols:
            schema |= {c: pl.Datetime for c in self.timestamp_cols}
        return schema

    def _read_excel(self, stream, source):
        try:
            frame = pl.read_excel(
                stream,
                sheet_name=self.sheet_name,
                has_header=True,
                schema_overrides=self.build_schema(),
                read_options={"header_row": self.header_row},
            ).lazy()

            return LoadResult(
                frame=frame,
                context={
                    "source": source,
                    "sheet": self.sheet_name,
                    "loader": self.__class__.__name__,
                },
            )
        except Exception as e:
            print(f"Error Reading Excel file {e}")
            return LoadResult(frame=pl.LazyFrame(), context={})

    def _read_csv(self, stream, source):
        try:
            frame = pl.scan_csv(stream, schema_overrides=self.build_schema())
            return LoadResult(
                frame=frame,
                context={
                    "source": source,
                    "sheet": self.sheet_name,
                    "loader": self.__class__.__name__,
                },
            )
        except Exception as e:
            print(f"Error Reading CSV file {e}")
            return LoadResult(frame=pl.LazyFrame(), context={})

    def _load_from_stream(self, stream_data: bytes | IO[bytes], file_name: str):
        for name, stream in stream_data.items():
            if name.split(".")[-1] == "xlsx":
                return self._read_excel(stream, name)

            if name.split(".")[-1] == "csv":
                return self._read_csv(stream, name)

    def _load_from_path(self, path: str):
        p = Path(path)
        if not p.exists():
            print(f"{p} does not exist")
            return LoadResult(frame=pl.LazyFrame(), context={})

        suffix = p.suffix.lower()
        if suffix == ".xlsx":
            return self._read_excel(p, p.name)
        if suffix == ".csv":
            return self._read_csv(p, p.name)

        return LoadResult(frame=pl.LazyFrame(), context={})

    def load(self, path: str | Path | None = None, **kwargs) -> LoadResult:
        """
        统一入口。

        Resolution order:
          1. Explicit ``path`` parameter.
          2. ``search_dir`` kwarg — scan directory for the most recent file.
          3. ``byte`` + ``name`` kwargs (API upload / in-memory).
          4. Class-level ``file_name`` default.
          5. Empty result fallback.
        """
        # 1. search_dir → resolve to a concrete path
        if path is None:
            search_dir = kwargs.pop("search_dir", None)
            if search_dir is not None:
                path = self._find_latest_file(Path(search_dir))

        # 2. Explicit path (or resolved from search_dir)
        if path:
            return self._load_from_path(path)

        # 3. Byte stream (API upload)
        if "byte" in kwargs:
            byte_data = kwargs["byte"]
            file_name = kwargs.get("name")
            if byte_data and file_name:
                return self._load_from_stream(byte_data, file_name)

        # 4. Class-level default file_name
        if self.file_name:
            default_path = self.data_path / self.file_name
            return self._load_from_path(default_path)

        # 5. Fallback
        return LoadResult(frame=pl.LazyFrame(), context={})

    @staticmethod
    def _find_latest_file(directory: Path, glob_pattern: str = "*.xlsx") -> Path | None:
        """Return the most recently modified file matching *glob_pattern* in *directory*."""
        if not directory.exists():
            return None
        files = sorted(
            directory.glob(glob_pattern), key=lambda p: p.stat().st_mtime, reverse=True
        )
        return files[0] if files else None

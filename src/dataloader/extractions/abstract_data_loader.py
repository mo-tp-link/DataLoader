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
        用法:
        1. loader.load("data.csv")
        2. loader.load(path="data.xlsx")
        3. loader.load(byte=file_bytes, name="upload.xlsx")
        """

        # 1. 优先检查显式的 path 参数
        if path:
            return self._load_from_path(path)

        # 2. 检查 kwargs 中的 byte 流 (通常用于 API 上传或内存处理)
        # 需要同时提供 'byte' 和 'name' (为了判断格式)
        if "byte" in kwargs:
            byte_data = kwargs["byte"]
            file_name = kwargs.get("name")

            if byte_data and file_name:
                return self._load_from_stream(byte_data, file_name)

        # 3. 如果都没有，尝试使用类属性定义的默认 file_name
        if self.file_name:
            print("Reading file name")
            default_path = self.data_path / self.file_name
            # 这里加个 exists check 防止报错，或者让 _load_from_path 处理
            return self._load_from_path(default_path)

        # 4. 兜底返回空结果
        return LoadResult(frame=pl.LazyFrame(), context={})

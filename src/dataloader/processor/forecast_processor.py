import polars as pl

from dataloader.schemas.forecast_schema import build_forecast_schema
from dataloader.utils import LoadResult
from .abstract_processor import ProcessorAbstract


class ForecastProcessor(ProcessorAbstract):
    def process(self, lr: LoadResult | None, *args, **kwargs) -> LoadResult | None:
        # if "pos" in kwargs.keys():
        #     pos = kwargs['pos']
        out = lr.frame.rename(self.clean_col_name)
        schema = build_forecast_schema(out)
        out = out.with_columns(pl.col(schema.forecast_cols).cast(pl.Int64))

        lr.add(schema=schema)
        return LoadResult(frame=out, context=lr.context)

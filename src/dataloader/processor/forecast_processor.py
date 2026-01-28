import polars as pl

from datetime import datetime, timedelta
from dataloader.schemas.forecast_schema import build_forecast_schema
from dataloader.utils import LoadResult
from .abstract_processor import ProcessorAbstract


class ForecastProcessor(ProcessorAbstract):
    def convert_to_weekly(self, fcst):
        pass

    def lazy_build_weekly_df(self, year=2024, month=11, day=1, n_weeks_after_today=100):
        """
        Builds a Polars DataFrame with date, week_start, and week_end columns.
        Weeks are defined as starting on Sunday.
        """
        start_date = datetime(year=year, month=month, day=day)
        end_date = datetime.today() + timedelta(weeks=n_weeks_after_today)

        # Base DataFrame with a date range
        date_df = pl.LazyFrame(
            {
                "date": pl.date_range(
                    start=start_date, end=end_date, interval="1d", eager=True
                )
            }
        )

        return date_df.with_columns(
            # Shift date by +1, truncate to Monday, then shift back -1 to get Sunday
            week_start=(
                pl.col("date").dt.offset_by("1d").dt.truncate("1w").dt.offset_by("-1d")
            ),
        ).with_columns(
            # The week_end is always 6 days after the week_start
            week_end=pl.col("week_start").dt.offset_by("6d"),
        )

    def process(self, lr: LoadResult | None, *args, **kwargs) -> LoadResult | None:
        # if "pos" in kwargs.keys():
        #     pos = kwargs['pos']
        out = lr.frame.rename(self.clean_col_name).with_columns(
            pl.col(pl.Float64).fill_null(0.0),
            cap_name=self.clean_cap_name("mfg"),
        )

        schema = build_forecast_schema(out)
        print(schema)
        out = out.with_columns(pl.col(schema.forecast_cols).cast(pl.Int64))

        agg = out.group_by(["inv", "cap_name"]).agg(
            pl.col(schema.forecast_cols + schema.presentation_cols).sum(), pl.col("clt")
        )

        lr.add(schema=schema, agg=agg)

        return LoadResult(frame=out, context=lr.context)

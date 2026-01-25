from dataloader.schemas import AMZPriceSchema
from dataloader.utils import LoadResult
from .abstract_processor import ProcessorAbstract


class AMZPriceProcessor(ProcessorAbstract):
    schema_cls = AMZPriceSchema

    def process(self, lr: LoadResult | None, **kwargs) -> LoadResult | None:
        schema = self.schema_cls()

        if lr is None:
            return None

        out = (
            lr.frame.with_columns(cap_name=self.clean_cap_name("product_name"))
            .rename({"product_name": "Item Model"})
            .rename(self.clean_col_name)
        )
        asin_pair = out.select(["asin", "cap_name"]).unique()
        lr.add(schema= schema, cap_name_pair = asin_pair)
        out = out.select(schema.all_cols)
        return LoadResult(frame=out, context=lr.context)

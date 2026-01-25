from dataloader.schemas import PriceSchema
from dataloader.utils import LoadResult
from .abstract_processor import ProcessorAbstract


class PriceProcessor(ProcessorAbstract):
    schema_cls = PriceSchema

    def process(self, lr: LoadResult | None, **kwargs) -> LoadResult | None:
        schema = self.schema_cls()

        if lr is None:
            return None

        out = (
            lr.frame.with_columns(cap_name=self.clean_cap_name("Product Name"))
            .rename({"Product Name": "Item Model"})
            .rename(self.clean_col_name)
        )
        cap_name_pair = out.select(["item_model", "cap_name"]).unique()
        lr.add(schema= schema, cap_name_pair = cap_name_pair)
        out = out.select(schema.all_cols)
        return LoadResult(frame=out, context=lr.context)

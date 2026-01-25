from dataloader.schemas import SPASchema
from dataloader.utils import LoadResult
from .abstract_processor import ProcessorAbstract


class SPAProcessor(ProcessorAbstract):
    schema_cls = SPASchema

    def process(self, lr: LoadResult | None, **kwargs) -> LoadResult | None:
        schema = self.schema_cls()

        if lr is None:
            return None

        out = (
            lr.frame.with_columns(
                cap_name=self.clean_cap_name("Product Name"),
                cap_cust=self.clean_company_name("Reseller Name"),
            )
            .rename({"Product Name": "Item Model"})
            .rename(self.clean_col_name)
        )
        cap_name_pair = out.select(["item_model", "cap_name"]).unique()
        cap_cust_pair = out.select(["reseller_name", "cap_cust"]).unique()

        out = out.select(schema.all_cols)
        lr.add(schema=schema, cap_name_pair=cap_name_pair, cap_cust_pair=cap_cust_pair)

        return LoadResult(frame=out, context=lr.context)

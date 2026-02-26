import polars as pl
import re
def clean_cap_name( col) -> pl.Expr:
    return (
        pl.col(col)
        .str.strip_chars()
        .str.to_uppercase()
        .str.replace_all(r"[^A-Z0-9+]", "")
        .alias("cap_name")
    )

def clean_company_name( col) -> pl.Expr:
    return (
        pl.col(col)
        .str.strip_chars()
        .str.to_uppercase()
        .str.replace_all(r"[^A-Z0-9]", "")
        .alias("cap_cust")
    )

def clean_col_name(c):
    pattern = r"[^A-Za-z0-9]"
    return re.sub(r"_+", "_", re.sub(pattern, "_", c)).lower().strip("_")

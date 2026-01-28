import polars as pl

path = "/mnt/c/Users/Mo/OneDrive - TP-Link/Keeper of the Endless Stock, Warden of the Supply Realms, Master of Replenishment, Breaker of Stockouts, Tamer of Chaos and Crates's Shared Folder/Forecast Shared.xlsx"


forecast_dict = pl.read_excel(path, sheet_id=0)



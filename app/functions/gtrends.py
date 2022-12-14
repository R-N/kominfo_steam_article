import streamlit as st
import pandas as pd
from ..global_data import Constants
import plotly.express as px
from numerize import numerize
from ..functions.util import sorted_keys

LABELS = {
    "indo_daily": "Tren harian indonesia",
    "indo_hourly": "Tren per-jam indonesia",
    "world_daily": "Tren harian dunia",
    "world_hourly": "Tren per-jam dunia",
}
EXCLUDE_COLS = [
    "kominfo judi",
    "kominfo bom",
    "kominfo serang",
    "kominfo slot"
]
DEFAULT_COLS_1 = [
    "kominfo",
    "kominfo block",
    "kominfo blokir",
    "kominfo pse",
    "kominfo steam",
    "#BlokirKominfo"
]
DEFAULT_COLS_2 = [
    "vpn",
    "unblock",
    "tunnel",
    "dns",
    "dpi tunnel"
]

st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id})
def load_df(sheet, excel_path=Constants.gtrends_path, exclude_cols=EXCLUDE_COLS):
    df = pd.read_excel(excel_path, sheet_name=sheet)
    df = df.set_index("Day" if "Day" in df.columns else "Time")
    df = df.drop(exclude_cols, axis=1)
    return df
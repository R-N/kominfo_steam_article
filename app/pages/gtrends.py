import streamlit as st
import pandas as pd
from ..global_data import Constants
import plotly.express as px
from numerize import numerize
from ..functions.util import sorted_keys, selectbox_2

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
LABELS = {
    "indo_daily": "Tren harian indonesia",
    "indo_hourly": "Tren per-jam indonesia",
    "world_daily": "Tren harian dunia",
    "world_hourly": "Tren per-jam dunia",
}
def app():
    sheet = selectbox_2(st, "Google Trends", LABELS, default="indo_hourly")
    df = pd.read_excel(Constants.gtrends_path, sheet_name=sheet)
    df = df.set_index("Day" if "Day" in df.columns else "Time")
    df = df.drop(EXCLUDE_COLS, axis=1)
    fig = df.plot()
    fig.for_each_trace(
        lambda trace: trace.update(visible="legendonly") 
            if trace.name not in DEFAULT_COLS_1 else ()
    )
    st.plotly_chart(fig, use_container_width=True)
    fig = df.plot()
    fig.for_each_trace(
        lambda trace: trace.update(visible="legendonly") 
            if trace.name not in DEFAULT_COLS_2 else ()
    )
    st.plotly_chart(fig, use_container_width=True)
    

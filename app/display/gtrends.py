import streamlit as st
import pandas as pd
from ..global_data import Constants
import plotly.express as px
from numerize import numerize
from ..functions.util import sorted_keys
from ..display.util import selectbox_2, whitelist_plotly_vars
from ..functions.gtrends import load_df, DEFAULT_COLS_1

LABELS = {
    "indo_daily": "Tren harian indonesia",
    "indo_hourly": "Tren per-jam indonesia",
    "world_daily": "Tren harian dunia",
    "world_hourly": "Tren per-jam dunia",
}

def trend_line(df, whitelist=DEFAULT_COLS_1):
    fig = df.plot(labels={"value": "Tren", **LABELS, **labels})
    if whitelist:
        whitelist_plotly_vars(fig, whitelist)
    st.plotly_chart(fig, use_container_width=True)
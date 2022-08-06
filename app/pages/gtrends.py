import streamlit as st
import pandas as pd
from ..global_data import Constants
import plotly.express as px
from numerize import numerize
from ..functions.util import sorted_keys
from ..display.util import selectbox_2
from ..functions.gtrends import DEFAULT_COLS_1, DEFAULT_COLS_2, LABELS
from ..functions.gtrends import load_df
from ..display.gtrends import trend_line


st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id, Constants.container_type: id})
def gtrends_section(
    container, 
    sheet="indo_hourly", 
    labels=LABELS, 
    whitelist=DEFAULT_COLS_2,
    compact=True, 
    key="default"
):
    con = container.container()
    with container.expander("Opsi") as exp:
        sheet = selectbox_2(st, "Google Trends", labels, default="indo_hourly")
    df = load_df(sheet)
    if not compact:
        con = container.container()
    trend_line(con, df, whitelist=whitelist)

def app():
    sheet = selectbox_2(st, "Google Trends", LABELS, default="indo_hourly")
    df = load_df(sheet)
    trend_line(st, df, whitelist=DEFAULT_COLS_1)
    trend_line(st, df, whitelist=DEFAULT_COLS_2)
    

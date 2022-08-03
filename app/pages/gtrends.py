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

def app():
    sheet = selectbox_2(st, "Google Trends", LABELS, default="indo_hourly")
    df = load_df(sheet)
    trend_line(st, df, whitelist=DEFAULT_COLS_1)
    trend_line(st, df, whitelist=DEFAULT_COLS_2)
    

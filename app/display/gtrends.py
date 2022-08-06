import streamlit as st
import pandas as pd
from ..global_data import Constants
import plotly.express as px
from numerize import numerize
from ..functions.util import sorted_keys
from ..display.util import selectbox_2, whitelist_plotly_vars, fig_defaults
from ..functions.gtrends import load_df, DEFAULT_COLS_1, LABELS


def trend_line(container, df, whitelist=DEFAULT_COLS_1, labels={}):
    fig = df.plot(labels={"value": "Tren", **labels})
    fig_defaults(fig)
    if whitelist:
        whitelist_plotly_vars(fig, whitelist)
    container.plotly_chart(fig, use_container_width=True)
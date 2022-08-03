import streamlit as st
import pandas as pd
import plotly.express as px
from ..global_data import Constants
from ..functions.twitter import POLARITY_LABEL_COLS, POLARITY_LABEL_VOLUME_COLS, LABELS, DEFAULT_QUERIES
from ..functions.twitter import load_all, aggregate_data, filter_query
from ..display.util import whitelist_plotly_vars

def tweet_volume_bar_stack(container, df, y, labels={}):
    fig = px.bar(
        df,  
        y=y,
        labels={"value": "Volume", **LABELS, **labels}
    )
    container.plotly_chart(fig, use_container_width=True)

def tweet_polarity_line(container, df, cols, labels={}):
    fig = df[cols].plot(labels={**LABELS, **labels})
    container.plotly_chart(fig, use_container_width=True)

def tweet_polarity_line_2(container, df, whitelist=DEFAULT_QUERIES, labels={}):
    fig = df.plot(labels={"value": "Polaritas Sentimen", **LABELS, **labels})
    if whitelist:
        whitelist_plotly_vars(fig, whitelist)
    container.plotly_chart(fig, use_container_width=True)

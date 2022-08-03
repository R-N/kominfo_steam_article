import streamlit as st
import pandas as pd
import plotly.express as px
from ..global_data import Constants
from ..functions.twitter import POLARITY_LABEL_COLS, POLARITY_LABEL_VOLUME_COLS, QUERIES, DATES, EXCLUDE_QUERIES
from ..functions.twitter import load_all, aggregate_data, filter_query
from ..display.twitter import tweet_volume_bar_stack, tweet_polarity_line, tweet_polarity_line_2
from ..display.util import selectbox_2


def app():
    col1, col2, col3 = st.columns(3)
    neutral_bin_min = col1.number_input(
        "Minimum Sentimen Netral",
        min_value=-1.0,
        max_value=0.0,
        value=-1.0/3.0,
        step=0.1
    )
    neutral_bin_max = col2.number_input(
        "Maximum Sentimen Netral",
        min_value=0.0,
        max_value=1.0,
        value=1.0/3.0,
        step=0.1
    )
    min_subjectivity = col3.number_input(
        "Minimum Subjectivity",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1
    )
    all_data = load_all(sentiment_bins=(neutral_bin_min, neutral_bin_max))
    aggregate = aggregate_data(all_data, min_subjectivity=min_subjectivity)

    col1, col2 = st.columns(2)
    query = selectbox_2(
        col1, 
        "Query", 
        {k:k for k in QUERIES if k not in EXCLUDE_QUERIES}, 
        default="kominfo"
    )
    volume = selectbox_2(col2, "Volume", {
        "volume": "Dikali like/rt",
        "count": "Hanya jumlah"
    }, default="volume")

    df_q = filter_query(aggregate, query)

    y = POLARITY_LABEL_VOLUME_COLS if volume=="volume" else POLARITY_LABEL_COLS
    tweet_volume_bar_stack(st, df_q, y)

    col1, col2 = st.columns(2)
    volume = selectbox_2(col1, "Volume", {
        "volume": "Dikali like/rt",
        "polarity": "Hanya polaritas"
    }, default="volume")
    neutral = selectbox_2(col2, "Netral", {
        "include": "Dihitung",
        "exclude": "Tidak dihitung"
    }, default="exclude")

    value = "{0}_polarity{1}".format(
        "volume" if volume=="volume" else "mean",
        "_no_neutral" if neutral=="exclude" else ""
    )

    df_q = pd.pivot_table(
        aggregate, 
        values=value, 
        index="date",
        columns="query"
    )
    tweet_polarity_line_2(st, df_q)


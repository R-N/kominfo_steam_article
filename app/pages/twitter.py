import streamlit as st
import pandas as pd
import plotly.express as px
from ..global_data import Constants
from ..functions.twitter import DEFAULT_MIN_SUBJECTIVITY, POLARITY_LABEL_COLS, POLARITY_LABEL_VOLUME_COLS, QUERIES, DATES, EXCLUDE_QUERIES, DEFAULT_NEUTRAL_BINS, DEFAULT_MIN_SUBJECTIVITY
from ..functions.twitter import load_all, aggregate_data, filter_query, get_tweet
from ..display.twitter import tweet_volume_bar_stack, tweet_polarity_line, tweet_polarity_line_2, display_tweet, tweet_slides
from ..display.util import selectbox_2, multiselect_2
from numerize import numerize

def aggregate_section(aggregate):
    

    col1, col2 = st.columns(2)
    query = selectbox_2(
        col1, 
        "Query", 
        {k:k for k in QUERIES if k not in EXCLUDE_QUERIES}, 
        default="kominfo",
        key="count"
    )
    count = selectbox_2(col2, "Jumlah", {
        "count": "Hanya tweet original",
        "count_rt": "Tweet + Retweet",
        "count_rt_quote": "Tweet + Retweet + Quote"
    }, default="count_rt")

    df_q = filter_query(aggregate, query)
    tweet_volume_bar_stack(st, df_q, count)

    col1, col2 = st.columns(2)
    query = selectbox_2(
        col1, 
        "Query", 
        {k:k for k in QUERIES if k not in EXCLUDE_QUERIES}, 
        default="kominfo",
        key="sentiment"
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
    }, default="include")

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

def tweet_section(all_data):
    col1, col2 = st.columns(2)
    sorting = selectbox_2(
        col1,
        "Sort by",
        {
            "Sorttt": "sotrtrt"
        },
        default="Sorttt"
    )
    limit = col2.number_input(
        "Limit",
        min_value=0,
        max_value=100,
        value=10,
        step=1
    )
    con = st.container()
    queries = [k for k in QUERIES if k not in EXCLUDE_QUERIES]
    dates = DATES
    if st.checkbox("Filter"):
        queries = multiselect_2(
            st, 
            "Query", 
            {k:k for k in queries}, 
            default=queries
        )
        dates = multiselect_2(
            st, 
            "Tanggal", 
            {k:k for k in dates}, 
            default=dates
        )
    ids = [901048172738482176] * 10
    tweet_slides(con, ids, key="twitter")
    

def app():

    col1, col2, col3 = st.sidebar.columns(3)
    neutral_bin_min = st.sidebar.number_input(
        "Minimum Sentimen Netral",
        min_value=-1.0,
        max_value=0.0,
        value=DEFAULT_NEUTRAL_BINS[0],
        step=0.1
    )
    neutral_bin_max = st.sidebar.number_input(
        "Maximum Sentimen Netral",
        min_value=0.0,
        max_value=1.0,
        value=DEFAULT_NEUTRAL_BINS[1],
        step=0.1
    )
    min_subjectivity = st.sidebar.number_input(
        "Minimum Subjectivity",
        min_value=0.0,
        max_value=1.0,
        value=DEFAULT_MIN_SUBJECTIVITY,
        step=0.1
    )
    all_data = load_all(sentiment_bins=(neutral_bin_min, neutral_bin_max))
    aggregate = aggregate_data(all_data, min_subjectivity=min_subjectivity)

    with st.expander("Agregat", expanded=True):
        aggregate_section(aggregate)

    with st.expander("Top Tweets", expanded=True):
        tweet_section(all_data)
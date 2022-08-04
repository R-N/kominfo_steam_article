import streamlit as st
import pandas as pd
import plotly.express as px
from ..global_data import Constants
from ..functions.twitter import DEFAULT_MIN_SUBJECTIVITY, POLARITY_LABEL_COLS, POLARITY_LABEL_VOLUME_COLS, QUERIES, DATES, EXCLUDE_QUERIES, DEFAULT_NEUTRAL_BINS, DEFAULT_MIN_SUBJECTIVITY, LABELS, INCLUDE_QUERIES
from ..functions.twitter import load_all, aggregate_data, filter_query, get_tweet, merge_data
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

def tweet_section(container, all_data, sentiment="all", queries=INCLUDE_QUERIES, dates=DATES, sorting="engagement", limit=10):
    con1 = container.container()
    con2 = container.container()
    if container.checkbox("Filter"):
        sentiment = selectbox_2(
        container,
        "Sentimen",
        {
            k: LABELS[k]
            for k in [
                "positive",
                "neutral",
                "negative",
                "all"
            ]
        },
        default=sentiment
    )
        queries = multiselect_2(
            container, 
            "Query", 
            {k:k for k in queries}, 
            default=queries
        )
        dates = multiselect_2(
            container, 
            "Tanggal", 
            {k:k for k in dates}, 
            default=dates
        )
    merged = merge_data(all_data, queries, dates)
    if sentiment != "all":
        merged = merged[merged["sentiment_label"]==LABELS[sentiment]]
    col1, col2, col3 = con1.columns(3)
    sorting = selectbox_2(
        col2,
        "Sort by",
        {
            k: LABELS[k]
            for k in [
                "like_count",
                "reply_count",
                "retweet_count",
                "quote_count",
                "engagement"
            ]
        },
        default=sorting
    )
    limit = col3.number_input(
        "Limit",
        min_value=1,
        max_value=100,
        value=limit,
        step=1
    )
    limit = max(0, min(100, limit))
    merged = merged.sort_values(sorting, ascending=False).iloc[:int(limit)].reset_index()
    #st.dataframe(merged)
    tweets = merged.to_dict('records')
    #st.write(tweets)
    
    tweet_count = len(tweets)
    index = col1.number_input(
        "Tweet #",
        min_value=1,
        max_value=tweet_count,
        value=1,
        step=1
    )
    index = int(index) - 1
    index = max(0, min(tweet_count - 1, index))
    #tweet_slides(con2, tweets, key="twitter")
    
    tweet = tweets[index]
    display_tweet(con2, tweet, "Top Tweet #{0}".format(index+1))
    

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
        tweet_section(st, all_data)
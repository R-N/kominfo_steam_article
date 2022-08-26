import streamlit as st
import pandas as pd
import plotly.express as px
from ..global_data import Constants
from ..functions.twitter import DEFAULT_MIN_SENTIMENT_SCORE, POLARITY_LABEL_COLS, POLARITY_LABEL_VOLUME_COLS, QUERIES, DATES, EXCLUDE_QUERIES, LABELS, INCLUDE_QUERIES
from ..functions.twitter import load_all, aggregate_data, filter_query, get_tweet, merge_data
from ..display.twitter import tweet_volume_bar_stack, tweet_polarity_line, tweet_polarity_line_2, display_tweet, tweet_slides, tweet_volume_line
from ..display.util import selectbox_2, multiselect_2
from numerize import numerize


st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id, Constants.container_type: id})
def sentiment_section(
    container, 
    aggregate, 
    query="kominfo", 
    volume="volume", 
    chart="bar",
    compact=False,
    key="sentiment"
):
    con = container.container() if compact else container
    def option_section(
        col1, col2, col3,
        query=query, volume=volume, chart=chart
    ):
        query = selectbox_2(
            col1, 
            "Query", 
            {k:k for k in INCLUDE_QUERIES}, 
            default=query,
            key=key
        )
        volume = selectbox_2(col2, "Volume", {
            "volume": "Dikali like/rt",
            "count": "Hanya jumlah"
        }, default=volume, key=key + "2")
        labels = POLARITY_LABEL_VOLUME_COLS if volume=="volume" else POLARITY_LABEL_COLS
        chart = selectbox_2(col3, "Grafik", {
            "bar": "Bar chart",
            "line": "Line chart"
        }, default=chart, key=key + "3")
        return query, labels, chart

    if compact:
        with container.expander("Opsi"):
            query, labels, chart = option_section(st, st, st)
    else:
        query, labels, chart = option_section(*container.columns(3))
    df_q = filter_query(aggregate, query)
    f = tweet_volume_bar_stack if chart == "bar" else tweet_volume_line
    f(con, df_q, labels)



st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id, Constants.container_type: id})
def volume_section(
    container, 
    aggregate, 
    query="kominfo", 
    count="count", 
    chart="bar",
    compact=False,
    key="volume"
):
    con = container.container() if compact else container
    def option_section(
        col1, col2, col3, 
        query=query, count=count, chart=chart
    ):
        query = selectbox_2(
            col1, 
            "Query", 
            {k:k for k in QUERIES if k not in EXCLUDE_QUERIES}, 
            default=query,
            key=key
        )
        count = selectbox_2(col2, "Jumlah", {
            "count": "Hanya tweet original",
            "count_rt": "Tweet + Retweet",
            "count_rt_quote": "Tweet + Retweet + Quote"
        }, default=count, key=key+"2")
        chart = selectbox_2(col3, "Grafik", {
            "bar": "Bar chart",
            "line": "Line chart"
        }, default=chart, key=key+"3")
        return query, count, chart

    if compact:
        with container.expander("Opsi"):
            query, count, chart = option_section(st, st, st)
    else:
        query, count, chart = option_section(*container.columns(3))
    df_q = filter_query(aggregate, query)
    f = tweet_volume_bar_stack if chart == "bar" else tweet_volume_line
    f(con, df_q, count)


def polarity_section(
    container, 
    aggregate,
    volume="volume",
    neutral="include",
    compact=False
):
    con = container.container() if compact else container
    
    def option_section(col1, col2, volume=volume, neutral=neutral):
        volume = selectbox_2(col1, "Volume", {
            "volume": "Dikali like/rt",
            "polarity": "Hanya polaritas"
        }, default=volume)
        neutral = selectbox_2(col2, "Netral", {
            "include": "Dihitung",
            "exclude": "Tidak dihitung"
        }, default=neutral)
        value = "{0}_polarity{1}".format(
            "volume" if volume=="volume" else "mean",
            "_no_neutral" if neutral=="exclude" else ""
        )
        return value, neutral

    if compact:
        with container.expander("Opsi"):
            value, neutral = option_section(st, st)
    else:
        value, neutral = option_section(*container.columns(2))

    df_q = pd.pivot_table(
        aggregate, 
        values=value, 
        index="date",
        columns="query"
    )
    tweet_polarity_line_2(con, df_q)

def aggregate_section(container, aggregate):

    container.markdown("## Tweet Volume")
    volume_section(
        container,
        aggregate
    )

    container.markdown("## Tweet Sentiment Volume")
    sentiment_section(
        container,
        aggregate
    )
    """
    container.markdown("## Tweet Polarity")
    polarity_section(
        container,
        aggregate
    )
    """


st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id, Constants.container_type: id})
def tweet_section(
    container, 
    all_data, 
    sentiment="all", 
    queries=INCLUDE_QUERIES, 
    dates=DATES, 
    sorting="engagement", 
    limit=10, 
    show=1,
    compact=False,
    key="tweet"
):
    con = container.container() if compact else container
    def option_section(
        col2, col3, col4, col5,
        sentiment=sentiment,
        sorting=sorting,
        limit=limit,
        show=show
    ):
        sentiment = selectbox_2(
            col2,
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
            default=sentiment,
            key=key
        )
        sorting = selectbox_2(
            col3,
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
            default=sorting,
            key=key + "2"
        )
        limit = col4.number_input(
            "Limit",
            min_value=1,
            max_value=100,
            value=limit,
            step=1,
            key=key + "3"
        )
        limit = int(limit)
        limit = max(1, min(100, limit))
        
        show = col5.number_input(
            "Show",
            min_value=1,
            max_value=limit,
            value=show,
            step=1,
            key=key + "4"
        )
        show = int(show)
        show = max(1, min(limit, show))

        return sentiment, sorting, limit, show

    if not compact:
        sentiment, sorting, limit, show = option_section(*container.columns(4))
    with container.expander("Opsi"):
        if compact:
            sentiment, sorting, limit, show = option_section(*st.columns(4))
        queries = multiselect_2(
            st, 
            "Query", 
            {k:k for k in queries}, 
            default=queries,
            key=key + "5"
        )
        dates = multiselect_2(
            st, 
            "Tanggal", 
            {k:k for k in dates}, 
            default=dates,
            key=key + "6"
        )
    merged = merge_data(all_data, queries, dates)
    if sentiment != "all":
        merged = merged[merged["sentiment_label"]==sentiment]

    merged = merged.sort_values(sorting, ascending=False).iloc[:int(limit)].reset_index()
    #st.dataframe(merged)
    tweets = merged.to_dict('records')
    #st.write(tweets)
    tweet_count = len(tweets)

    for i in range (0, show):
        display_tweet(con, tweets[i], "Top Tweet #{0}".format(i+1))
    if tweet_count > 0:
        with con.expander("Lihat tweet lainnya"):
            for i in range(show, tweet_count):
                display_tweet(st, tweets[i], "Top Tweet #{0}".format(i+1))


def app():

    st.sidebar.markdown("### Opsi data/grafik agregat")
    min_sentiment_score = st.sidebar.number_input(
        "Minimum Sentiment Confidence",
        min_value=0.0,
        max_value=100.0,
        value=DEFAULT_MIN_SENTIMENT_SCORE,
        step=10.0
    )
    all_data = load_all()
    aggregate = aggregate_data(all_data, min_sentiment_score=min_sentiment_score/100.0)

    st.markdown("# Agregat")
    aggregate_section(st, aggregate)

    st.markdown("# Top Tweets")
    tweet_section(st, all_data, show=3)
import streamlit as st
import pandas as pd
import plotly.express as px
from ..global_data import Constants
from ..functions.twitter import POLARITY_LABEL_COLS, POLARITY_LABEL_VOLUME_COLS, LABELS, DEFAULT_QUERIES
from ..functions.twitter import load_all, aggregate_data, filter_query, get_tweet
from ..display.util import whitelist_plotly_vars
from numerize import numerize


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


def display_tweet(container, tweet, title=None):
    con = container.container()
    if title:
        con.markdown("### Tweet #{0}".format(title))
    con.write(get_tweet(tweet["id"], tweet["text"]), unsafe_allow_html=True)
    col1, col2, col3, col4, col5, col6 = con.columns(6)
    col1.metric("Sentimen", tweet["sentiment_label"])
    col2.metric("Polarity", numerize.numerize(tweet["polarity"]))
    col3.metric("Like", numerize.numerize(float(tweet["like_count"])))
    col4.metric("Reply", numerize.numerize(float(tweet["reply_count"])))
    col5.metric("Retweet", numerize.numerize(float(tweet["retweet_count"])))
    col6.metric("Quote", numerize.numerize(float(tweet["quote_count"])))

def tweet_slides(con, tweets, key="default"):
    index = 0
    max_index = len(tweets)-1
    var = "tweet_slides_{0}".format(key)
    params = st.experimental_get_query_params()
    if var in params:
        index = int(params[var][0])
    else:
        con.experimental_set_query_params(**{var: index})
    tweet = tweets[index]
    display_tweet(con, tweet, index+1)
    col1, col2, col3 = con.columns((1, 10, 1))
    if col1.button("<"):
        st.experimental_set_query_params(**{var: max(0, min(max_index, index-1))})
    if col3.button(">"):
        st.experimental_set_query_params(**{var: max(0, min(max_index, index+1))})

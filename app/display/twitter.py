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


def display_tweet(container, id, title=None):
    con = container.container()
    if title:
        con.markdown("# #{0}".format(title))
    con.write(get_tweet(id), unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = con.columns(5)
    col1.metric("Polarity", numerize.numerize(0.5))
    col2.metric("Like", numerize.numerize(1))
    col3.metric("Reply", numerize.numerize(1))
    col4.metric("Retweet", numerize.numerize(1))
    col5.metric("Quote", numerize.numerize(1))

def tweet_slides(con, ids, key="default"):
    index = 0
    var = "tweet_slides_{0}".format(key)
    params = st.experimental_get_query_params()
    if var in params:
        index = int(params[var][0])
    else:
        st.experimental_set_query_params(**{var: index})
    tweet = ids[index]
    display_tweet(con, tweet, index)
    col1, col2, col3 = con.columns((1, 10, 1))
    if col1.button("<"):
        st.experimental_set_query_params(**{var: index-1})
    if col3.button(">"):
        st.experimental_set_query_params(**{var: index+1})

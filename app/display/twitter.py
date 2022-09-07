import streamlit as st
import pandas as pd
import plotly.express as px
from ..global_data import Constants
from ..functions.twitter import POLARITY_LABEL_COLS, POLARITY_LABEL_VOLUME_COLS, LABELS, DEFAULT_QUERIES
from ..functions.twitter import load_all, aggregate_data, filter_query, get_tweet
from ..display.util import whitelist_plotly_vars, fig_defaults
from numerize import numerize


def tweet_volume_bar_stack(container, df, y, labels={}):
    fig = px.bar(
        df,  
        y=y,
        labels={"value": "Volume Tweet", **LABELS, **labels},
        color_discrete_map={
            'positive_volume': '#2962FF',
            'positive': '#2962FF',
            'neutral_volume': '#B0BEC5',
            'neutral': '#B0BEC5',
            'negative_volume': '#D50000',
            'negative': '#D50000',
        }
    )
    fig_defaults(fig)
    container.plotly_chart(fig, use_container_width=True)

def tweet_volume_line(container, df, y, labels={}):
    fig = px.line(
        df,  
        y=y,
        labels={"value": "Volume", **LABELS, **labels},
        color_discrete_map={
            'positive_volume': '#2962FF',
            'positive': '#2962FF',
            'neutral_volume': '#B0BEC5',
            'neutral': '#B0BEC5',
            'negative_volume': '#D50000',
            'negative': '#D50000',
        },
        markers=True
    )
    fig_defaults(fig)
    container.plotly_chart(fig, use_container_width=True)

def tweet_polarity_line(container, df, cols, labels={}):
    fig = df[cols].plot(labels={**LABELS, **labels}, markers=True)
    fig_defaults(fig)
    container.plotly_chart(fig, use_container_width=True)

def tweet_polarity_line_2(container, df, whitelist=DEFAULT_QUERIES, labels={}):
    fig = df.plot(labels={"value": "Polaritas Sentimen", **LABELS, **labels}, markers=True)
    fig_defaults(fig)
    if whitelist:
        whitelist_plotly_vars(fig, whitelist)
    container.plotly_chart(fig, use_container_width=True)


def display_tweet(container, tweet, title=None):
    con = container.container()
    if title:
        con.markdown("### {0}".format(title))
    con.write(get_tweet(tweet["id"], tweet["text"]), unsafe_allow_html=True)
    col1, col2, col3, col4, col5, col6 = con.columns(6)
    col1.metric("Sentimen", LABELS[tweet["sentiment_label"]])
    col2.metric("Confidence", "{0:.2f}%".format(100*tweet["sentiment_score"]))
    col3.metric("Like", numerize.numerize(float(tweet["like_count"])))
    col4.metric("Reply", numerize.numerize(float(tweet["reply_count"])))
    col5.metric("Retweet", numerize.numerize(float(tweet["retweet_count"])))
    col6.metric("Quote", numerize.numerize(float(tweet["quote_count"])))

def tweet_slides(con, tweets, key="default"):
    max_index = len(tweets)-1
    index = con.number_input(
        "Tweet #",
        min_value=0,
        max_value=max_index,
        value=0,
        step=1
    )
    index = int(index)
    tweet = tweets[index]
    display_tweet(con, tweet, "Top Tweet #{0}".format(index+1))

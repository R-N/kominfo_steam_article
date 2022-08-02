import streamlit as st
import pandas as pd
from ..global_data import Constants
import plotly.express as px
from numerize import numerize
from ..functions.util import join_tag, groupby_tag, selectbox_2, multiselect_2, MySet
from ..functions.steam import CSV_COLS, LABELS
from ..functions.steam import split_by_availability, limit_df, show_metrics, groupby_tag_2, init_df
from ..functions.steam import game_availabiltiy_pie, game_histogram, game_bar_horizontal, game_scatter, collection_union_pie_2
import json
import functools

def section_game_availability(df, df_paid, df_free, df_unavailable, df_unreleased, appids):
    col1, col2 = st.columns(2)

    collection_union_pie_2(
        col1,
        df,
        appids,
        exclude=["both"]
    )

    game_availabiltiy_pie(
        col2,
        len(df_paid),
        len(df_free),
        len(df_unavailable),
        len(df_unreleased)
    )

    game_histogram(st, df_paid, "price_initial")



def section_game_estimated_revenue(df_paid, key="game"):
    positive_cb = st.checkbox("Hanya Review Positif", key=key)
    col = "estimated_revenue_positive" if positive_cb else "estimated_revenue"

    df, limit = limit_df(st, df_paid, col, key=key)

    show_metrics(st, df[col], 1)

    game_histogram(st, df, col)

    col_review = "total_positive" if positive_cb else "total_reviews"
    col1, col2 = st.columns(2)
    x = selectbox_2(col1, "x", {
        x: LABELS[x] for x in [
            "price_initial",
            col_review,
            "release_date"
        ] if x in df.columns
    }, default="price_initial")
    y = selectbox_2(col2, "y", {
        x: LABELS[x] for x in [
            "price_initial",
            col_review,
            "release_date",
            col
        ] if x in df.columns
    }, default=col_review)
    zs = multiselect_2(st, "z", {
        x: LABELS[x] for x in [
            col_review,
            col,
            "developers",
            "publishers"
        ] if x in df.columns
    }, default=[
        col,
        "review_summary",
        "developers",
        "publishers"
    ])

    game_scatter(st, df, x, y, zs)
    #df = df[[col]]
    game_bar_horizontal(st, df, col, "genres")

def section_grouped_estimated_revenue(df_paid):

    labels = {
        None: "Tanpa pengelompokan",
        "developers": "Developer",
        "publishers": "Publisher",
        #"categories": "Kategori",
        #"genres": "Genre",
        #"platforms": "Platform",
        #"supported_languages": "Bahasa",
    }

    df_grouped, grouping = groupby_tag_2(df_paid, labels)

    section_game_estimated_revenue(df_grouped, key=grouping)


def app():
    with open(Constants.steam_appid_path) as f:
        steam_appids = json.load(f)
    df = pd.read_excel(Constants.steam_path, sheet_name="data")
    df["count"] = 1
    init_df(df)
    df_paid, df_free, df_unavailable, df_unreleased = split_by_availability(df)

    # Game availability pie
    with st.expander("Ketersediaan Game"):
        section_game_availability(df, df_paid, df_free, df_unavailable, df_unreleased, steam_appids)

    with st.expander("Estimasi Pendapatan", expanded=True):
        section_grouped_estimated_revenue(df_paid)


import streamlit as st
import pandas as pd
from ..global_data import Constants
import plotly.express as px
from numerize import numerize
from ..functions.util import join_tag, groupby_tag, MySet
from ..display.util import selectbox_2, multiselect_2
from ..functions.steam import CSV_COLS, LABELS
from ..functions.steam import split_by_availability, init_df
from ..display.steam import game_availabiltiy_pie, show_metrics, game_histogram, game_bar_horizontal, game_scatter, collection_union_pie_2, limit_df, show_metrics_table, groupby_tag_2
import json
import functools



st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id, Constants.container_type: id})
def bar_horizontal_section(
    container, 
    df, 
    x="total_positive",
    y="genres",
    agg=True,
    x_options=[
        "price_initial",
        "total_reviews",
        "total_positive",
        "estimated_revenue",
        "estimated_revenue_positive",
        "count"
    ],
    y_options=[
        "genres",
        "categories",
        "platforms",
        "supported_languages",
        "supported_languages_voice"
    ],
    compact=False,
    key="default"
):
    con = container.container() if compact else container
    def option_section(
        col1, col2, con1,
        x=x, y=y, agg=agg,
        x_options=x_options, y_options=y_options,
        df=df, key=key
    ):
        x = selectbox_2(col1, "x", {
            x: LABELS[x] for x in x_options if x in df.columns
        }, default=x, key=key + "2")
        y = selectbox_2(col2, "y", {
            x: LABELS[x] for x in y_options if x in df.columns
        }, default=y, key=key + "3")
        agg = con1.checkbox("Agg", value=agg, key=key)
        return x, y, agg

    if compact:
        with container.expander("Opsi"):
            x, y, agg = option_section(st, st ,st)
    else:
        x, y, agg = option_section(*container.columns(2), container)
    game_bar_horizontal(
        con, df, x, y, 
        agg=agg
    )

st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id, Constants.container_type: id})
def scatter_section(
    container, df, 
    x="price_initial", 
    y="total_positive",
    zs=[
        "estimated_revenue",
        "estimated_revenue_positive",
        "review_summary",
        "developers",
        "publishers"
    ],
    x_options=[
        "price_initial",
        "total_reviews",
        "total_positive",
        "release_date"
    ],
    y_options=[
        "price_initial",
        "total_reviews",
        "total_positive",
        "release_date",
        "estimated_revenue",
        "estimated_revenue_positive",
    ],
    z_options=[
        "total_reviews",
        "total_positive",
        "estimated_revenue",
        "estimated_revenue_positive",
        "developers",
        "publishers"
    ],
    hlines=[],
    compact=False,
    key="default"
):
    con = container.container() if compact else container
    def option_section(
        col1, col2, con1,
        x=x, y=y, zs=zs,
        x_options=x_options,
        y_options=y_options,
        z_options=z_options,
        df=df
    ):
        x = selectbox_2(col1, "x", {
            x: LABELS[x] for x in x_options if x in df.columns
        }, default=x, key=key)
        y = selectbox_2(col2, "y", {
            x: LABELS[x] for x in y_options if x in df.columns
        }, default=y, key=key + "2")
        zs = multiselect_2(con1, "z", {
            x: LABELS[x] for x in z_options if x in df.columns
        }, default=zs, key=key + "3")
        return x, y, zs
    if compact:
        with container.expander("Opsi"):
            x, y, zs = option_section(st, st, st)
    else:
        x, y, zs = option_section(*container.columns(2), container)
    game_scatter(con, df, x, y, zs, hlines=hlines)

st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id, Constants.container_type: id})
def histogram_section(
    container, 
    df, 
    col="estimated_revenue_positive", 
    limit=None,
    metrics=True, 
    compact=False,
    nbins=5,
    height=360,
    x_options=[
        "price_initial",
        "total_reviews",
        "total_positive",
        "estimated_revenue",
        "estimated_revenue_positive"
    ],
    key="default"
):
    con = container.container() if compact else container
    def option_section(con1, con2, col=col, limit=limit, df=df):
        col = selectbox_2(con1, "x", {
            x: LABELS[x] for x in x_options if x in df.columns
        }, default=col, key=key)
        df, limit = limit_df(
            con2, 
            df, 
            col, 
            default=limit,
            compact=compact,
            key=key + "2"
        )
        return col, df, limit
    if compact:
        with container.expander("Opsi"):
            col, df, limit = option_section(st, st)
    else:
        col, df, limit = option_section(container, container)
    if metrics and not compact:
        show_metrics(con, df[col], 1, compact=compact)
    game_histogram(con, df, col, nbins=nbins, height=height)
    if metrics and compact:
        show_metrics_table(con, df[col], 1)

def game_availability_section(
    container, 
    df, 
    df_paid, 
    df_free, 
    df_unavailable, 
    df_unreleased, 
    appids,
    key="default"
):
    col1, col2 = container.columns(2)

    col1.markdown("## Data Game Terkumpul")
    collection_union_pie_2(
        col1,
        df,
        appids,
        exclude=["both"]
    )

    col2.markdown("## Ketersediaan Game")
    game_availabiltiy_pie(
        col2,
        len(df_paid),
        len(df_free),
        len(df_unavailable),
        len(df_unreleased)
    )

    container.markdown("## Harga Game")
    histogram_section(
        container, 
        df_paid,
        col="price_initial",
        x_options=["price_initial"],
        nbins=10, 
        key=key
    )



def game_estimated_revenue_section(
    container, 
    df, 
    key="steam"
):

    st.markdown("## Histogram")
    histogram_section(
        container, 
        df,
        nbins=10, 
        key=key
    )

    st.markdown("## Scatter Plot")
    scatter_section(
        container,
        df,
        key=key
    )

    st.markdown("## Horizontal Bar Chart")
    bar_horizontal_section(
        container,
        df,
        key=key
    )

def section_grouped_estimated_revenue(
    container, 
    df,
    key="steam"
):

    labels = {
        None: "Tanpa pengelompokan",
        "developers": "Developer",
        "publishers": "Publisher",
    }

    df_grouped, grouping = groupby_tag_2(
        container,
        df, 
        labels, 
        default=None,
        key=key
    )

    game_estimated_revenue_section(container, df_grouped, key=grouping)


def app():
    with open(Constants.steam_appid_path) as f:
        steam_appids = json.load(f)
    df = pd.read_excel(Constants.steam_path, sheet_name="data")
    df["count"] = 1
    init_df(df)
    df_paid, df_free, df_unavailable, df_unreleased = split_by_availability(df)

    # Game availability pie
    st.markdown("# Ketersediaan Game")
    game_availability_section(st, df, df_paid, df_free, df_unavailable, df_unreleased, steam_appids)

    st.markdown("# Estimasi Penjualan")
    section_grouped_estimated_revenue(st, df_paid)


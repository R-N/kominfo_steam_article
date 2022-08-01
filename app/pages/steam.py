import streamlit as st
import pandas as pd
from ..global_data import Constants
import plotly.express as px
from numerize import numerize
from ..util import sorted_keys, groupby_tag

CSV_COLS = [
    "categories",
    "developers",
    "dlc",
    "genres",
    "platforms",
    "publishers",
    "supported_languages"
]

def estimate_price(price, qty):
    s = price * qty
    # s.loc[~s.isna()] = s.loc[~s.isna()].astype(int)
    return s

def unpack_csv(df, cols):
    for col in cols:
        df[col] = df[col].str.split(',')
    return df

def split_by_availability(df):
    df_released = df[df["coming_soon"]==False]
    df_unreleased = df[df["coming_soon"]==True]

    df_paid = df[df["is_free"]==False]
    df_free = df[df["is_free"]==True]

    df_unavailable = df_paid[df_paid["price_initial"].isna()]
    df_paid = df_paid[~df_paid["price_initial"].isna()]

    df_paid.loc[:, "price_initial"] = df_paid["price_initial"] // 100
    df_paid.loc[:, "estimated_revenue"] = estimate_price(
        df_paid["price_initial"], 
        df_paid["total_reviews"]
    )
    df_paid.loc[:, "estimated_revenue_positive"] = estimate_price(
        df_paid["price_initial"], 
        df_paid["total_positive"]
    )

    return df_paid, df_free, df_unavailable, df_unreleased

def section_game_availability(df_paid, df_free, df_unavailable, df_unreleased):
    col1, col2 = st.columns((2, 4))

    df_pie = pd.DataFrame([
        ("Berbayar", len(df_paid)),
        ("Gratis", len(df_free)),
        ("Tidak tersedia lagi", len(df_unavailable)),
        ("Belum rilis", len(df_unreleased)),
    ], columns=["Kelompok", "Jumlah"])
    
    fig = px.pie(
        df_pie, 
        values='Jumlah', 
        names='Kelompok', 
        
    )
    fig.update_layout(legend=dict(
        yanchor="bottom",
        y=0.99,
        xanchor="left",
        x=0.01
    ))
    col1.plotly_chart(fig, use_container_width=True)

    fig = px.histogram(
        df_paid, 
        x="price_initial",
        labels={'x': 'Harga', 'y': 'Jumlah'}
    )
    fig.update_layout(bargap=0.30)
    col2.plotly_chart(fig, use_container_width=True)

def section_game_estimated_revenue(df_paid, key="game"):
    positive_cb = st.checkbox("Hanya Review Positif", key=key)
    col = "estimated_revenue_positive" if positive_cb else "estimated_revenue"

    limit_labels = {
        None: "Tanpa batas",
        50 * 10**6: "< 50 juta",
        20 * 10**6: "< 20 juta",
        5 * 10**6: "< 5 juta",
        2 * 10**6: "< 2 juta",
        1 * 10**6: "< 1 juta",
        500 * 10**3: "< 500 ribu",
        200 * 10**3: "< 200 ribu",
        "custom": "Custom"
    }
    col1, col2 = st.columns(2)
    limit = col1.selectbox(
        "Batas",
        [None, *sorted_keys(
            limit_labels, 
            condition=lambda x: isinstance(x, (int, float)), 
            reverse=True
        ), "custom"], 
        format_func=lambda x: limit_labels[x],
        key=key
    )

    if limit == "custom":
        limit = col2.number_input(
            "Batas",
            min_value=df_paid[col].min(),
            max_value=df_paid[col].max(),
            value=200.0 * 10**3,
            step=50.0 * 10**3
        )

    df = df_paid[df_paid[col] < limit] if limit else df_paid

    col1, col2, col3 = st.columns(3)
    col1.metric("Median", numerize.numerize(df[col].median()))
    col2.metric("Mean", numerize.numerize(df[col].mean()))
    col3.metric("Max", numerize.numerize(df[col].max()))

    fig = px.histogram(
        df,
        x=col,
        nbins=10,
        labels={col: 'Penjualan', 'count': 'Jumlah'}
    )
    fig.update_layout(bargap=0.30)
    st.plotly_chart(fig, use_container_width=True)

def section_grouped_estimated_revenue(df_paid):
    labels = {
        "developers": "Developer",
        "publishers": "Publisher",
        #"categories": "Kategori",
        #"genres": "Genre",
        #"platforms": "Platform",
        #"supported_languages": "Bahasa",
        None: "Tanpa pengelompokan"
    }
    grouping = st.selectbox(
        "Pengelompokan",
        [
            *sorted_keys(labels, condition=lambda x: isinstance(x, str)),
            None
        ],
        format_func=lambda x: labels[x]
    )

    df_grouped = groupby_tag(df_paid, grouping).sum() if grouping else df_paid

    section_game_estimated_revenue(df_grouped, key=grouping)

def app():
    df = pd.read_excel(Constants.steam_path, sheet_name="data")
    df = unpack_csv(df, CSV_COLS)
    df_paid, df_free, df_unavailable, df_unreleased = split_by_availability(df)

    st.dataframe(df_paid)
    # Game availability pie
    with st.expander("Ketersediaan Game"):
        section_game_availability(df_paid, df_free, df_unavailable, df_unreleased)

    with st.expander("Estimasi Pendapatan", expanded=True):
        section_grouped_estimated_revenue(df_paid)


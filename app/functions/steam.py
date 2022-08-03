import streamlit as st
import pandas as pd
from ..global_data import Constants
import plotly.express as px
from numerize import numerize
from ..functions.util import sorted_keys, groupby_tag, group_others, join_tag, MySet
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
import functools


CSV_COLS = [
    "categories",
    "developers",
    "dlc",
    "genres",
    "platforms",
    "publishers",
    "supported_languages"
]

LABELS = {
    "count": "Jumlah",
    "price_initial": "Harga",
    "total_reviews": "Jumlah review",
    "total_positive": "Jumlah review positif",
    "estimated_revenue": "Penjualan",
    "estimated_revenue_positive": "Penjualan positif",
    "review_summary": "Review",
    "release_date": "Tanggal rilis/debut",
    "developers": "Developer",
    "publishers": "Publisher",
    "genres": "Genre",
    "categories": "Kategori",
    "platforms": "Platform",
    "supported_languages": "Bahasa yang didukung",
    "supported_languages_voice": "Bahasa yang didukung penuh hingga suara"
}



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
    df_paid["release_date"] = pd.to_datetime(df_paid["release_date"])
    df_paid = df_paid.drop([
        "is_free",
        "coming_soon"
    ], axis=1)

    return df_paid, df_free, df_unavailable, df_unreleased


def limit_df(container, df_paid, col, key="default"):
    min_value=float(df_paid[col].min())
    max_value=float(df_paid[col].max())
    median = df_paid[col].median()
    
    limit_labels = {
        None: "Tanpa batas",
        50.0 * 10**6: "< 50 juta",
        20.0 * 10**6: "< 20 juta",
        10.0 * 10**6: "< 10 juta",
        5.0 * 10**6: "< 5 juta",
        2.0 * 10**6: "< 2 juta",
        1.0 * 10**6: "< 1 juta",
        500.0 * 10**3: "< 500 ribu",
        200.0 * 10**3: "< 200 ribu",
        "custom": "Custom"
    }
    limit_labels = {
        k: v for k, v in limit_labels.items() 
        if not isinstance(k, (int, float)) or (min_value <= k and k <= max_value)
    }
    col1, col2 = container.columns(2)
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
    step = 1.0
    while step < median:
        step *= 10
    step = step//10
    if limit == "custom":
        limit = col2.number_input(
            "Batas",
            min_value=min_value,
            max_value=max_value,
            value=median,
            step=step
        )

    df = df_paid[df_paid[col] < limit] if limit else df_paid

    return df, limit



def groupby_tag_2(df, labels, aggfunc=lambda x: x.sum()):
    grouping = st.selectbox(
        "Pengelompokan",
        [
            None,
            *sorted_keys(labels, condition=lambda x: isinstance(x, str))
        ],
        format_func=lambda x: labels[x],
        index=0
    )

    if grouping:
        df = df_g = groupby_tag(df, grouping)
        df = aggfunc(df)
        df["release_date"] = df_g["release_date"].min()
        rebuild_review(df)
    else:
        df = df.set_index("name")
    return df, grouping

def rebuild_review(df):
    df["positive_rate"] = df["total_positive"] / df["total_reviews"] * 100
    df["review_score_desc"] = df.apply(lambda x: 
        "{0} user reviews".format(int(x["total_reviews"])) if x["total_reviews"] < 10 else
        "Overwhelmingly Positive" if x["positive_rate"] >= 95 and x["total_reviews"] >= 500 else
        "Very Positive" if x["positive_rate"] >= 85 and x["total_reviews"] >= 50 else
        "Positive" if x["positive_rate"] >= 80 else
        "Mostly Positive" if x["positive_rate"] >= 70 else
        "Mixed" if x["positive_rate"] >= 40 else
        "Mostly Negative" if x["positive_rate"] >= 20 else
        "Negative" if x["total_reviews"] < 50 else
        "Very Negative" if x["total_reviews"] < 500 else
        "Overwhelmingly Negative",
        axis=1
    )
    summarize_review(df)
    return df

def summarize_review(df):
    df["review_summary"] = df.apply(
        lambda x: "{0} ({1:.2f}%)".format(x["review_score_desc"], x["positive_rate"]),
        axis=1
    )
    """
    df["review_summary"] = [
        "{0} ({1:.2f}%)".format(desc, rate)
        for desc, rate in df[["review_score_desc", "positive_rate"]].to_numpy()
    ]
    """
    return df

def split_languages(df):
    df["supported_languages_voice"] = df["supported_languages"].apply(
        lambda x: ([y[:-1] for y in x if y.endswith("*")])
    )
    df["supported_languages_voice"] = df["supported_languages_voice"].apply(
        lambda x: (x if x else ["No Voice"])
    )
    df["supported_languages"] = df["supported_languages"].apply(
        lambda x: ([y[:-1] if y.endswith("*") else y for y in x])
    )
    return df

def init_df(df):
    df = unpack_csv(df, CSV_COLS)
    df = split_languages(df)
    df = summarize_review(df)
    return df



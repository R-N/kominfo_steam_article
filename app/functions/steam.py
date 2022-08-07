import streamlit as st
import pandas as pd
from ..global_data import Constants
import plotly.express as px
from numerize import numerize
from ..functions.util import sorted_keys, groupby_tag, group_others, join_tag, MySet
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
import functools

COUNTRIES = {
    "bn": "Brunei",
    "id": "Indonesia",
    "mm": "Myanmar",
    "my": "Malaysia",
    "ph": "Filipina",
    "sg": "Singapura",
    "th": "Thailand",
    "vn": "Vietnam"
}

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
        df[col] = df[col].astype("str").str.split(',')
    return df

st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id})
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



st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id})
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

st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id})
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

st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id})
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

st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id})
def init_df(df, country="id"):
    if "dlc" not in df.columns:
        df["dlc"] = pd.Series([""]*len(df), index=df.index, name="dlc")
    df = unpack_csv(df, CSV_COLS)
    df = split_languages(df)
    df = summarize_review(df)
    df["country"] = country
    df["count"] = 1
    return df

st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id})
def merge_df(dfs):
    merged = pd.concat(dfs)
    #merged = merged[~merged.index.duplicated(keep='last')]
    return merged

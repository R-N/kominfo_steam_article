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
    "categories": "Kategori"
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
    min_value=df_paid[col].min()
    max_value=df_paid[col].max()
    
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

    if limit == "custom":
        limit = col2.number_input(
            "Batas",
            min_value=min_value,
            max_value=max_value,
            value=200.0 * 10**3,
            step=50.0 * 10**3
        )

    df = df_paid[df_paid[col] < limit] if limit else df_paid

    return df, limit


def show_metrics(container, series, metric_type=1):
    if metric_type==1:
        col1, col2, col3 = container.columns(3)
        col1.metric("Median", numerize.numerize(series.median()))
        col2.metric("Mean", numerize.numerize(series.mean()))
        col3.metric("Max", numerize.numerize(series.max()))


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
    df["supported_languages_voice"] = df.apply(
        lambda x: [y[:-1] for y in x["supported_languages"] if y.endswith("*")],
        axis=1
    )
    df["supported_languages"] = df.apply(
        lambda x: [y[:-1] if y.endswith("*") else y for y in x["supported_languages"]],
        axis=1
    )
    return df

def init_df(df):
    df = unpack_csv(df, CSV_COLS)
    df = split_languages(df)
    df = summarize_review(df)
    return df

def simple_pie(container, df, values="Jumlah", names="Kelompok", labels={}):
    
    fig = px.pie(
        df, 
        values=values, 
        names=names,
        labels={**LABELS, **labels}
    )
    fig.update_layout(legend=dict(
        yanchor="bottom",
        y=0.99,
        xanchor="left",
        x=0.01
    ))
    container.plotly_chart(fig, use_container_width=True)

def game_availabiltiy_pie(container, paid, free, unavailable, unreleased):
    
    df = pd.DataFrame([
        ("Berbayar", paid),
        ("Gratis", free),
        ("Tidak tersedia lagi", unavailable),
        ("Belum rilis", unreleased),
    ], columns=["Kelompok", "Jumlah"])

    simple_pie(container, df)

def game_scatter(container, df, x, y, zs, labels={}):
    zs = [
        pd.Series([numerize.numerize(x) for x in df[z].to_numpy()], name=z) 
        if (isinstance(z, (tuple, list)) and z[1]) or (is_numeric_dtype(df[z]) and df[z].max() > 10**3) else df[z]
        for z in zs
    ]
    labels = {**LABELS, **labels}
    fig = px.scatter(
        x=df[x],
        y=df[y],
        hover_name=df.index,
        hover_data=zs,
        #color=df["release_date"],
        labels={
            "x": labels[x],
            "y": labels[y],
            **{
                "hover_data_{0}".format(i): labels[zs[i].name]
                for i in range(len(zs))
            },
            **labels
        }
    )
    container.plotly_chart(fig, use_container_width=True)

def game_pie(container, df, col, threshold=0.01, others_name="Others", labels={}):
    total = df[col].sum()
    split = threshold * total
    big = df[df[col] >= split]
    others = df[df[col] < split]
    others = group_others(
        others, 
        others_name=others_name,
        list_cols=CSV_COLS
    )
    # rebuild_review(others)
    df2 = pd.concat([big, others])
    
    fig = px.pie(
        df2, 
        values=col, 
        names=df2.index,
        labels={**LABELS, **labels}
    )
    container.plotly_chart(fig, use_container_width=True)

def game_bar_horizontal(container, df, x, y, y_list=True, aggfunc=lambda x: x.sum(), labels={}):
    
    if y_list:
        df = join_tag(
            df,
            y
        )
        sorting = groupby_tag(df[[x, y]], y)
    else:
        sorting = df.groupby(y)
    sorting = aggfunc(sorting).sort_values(x, ascending=False)
    fig = px.bar(
        df, 
        x=x, 
        y=y, 
        #color=df2.index, 
        orientation='h',
        hover_data=[x],
        category_orders=sorting.index.to_list(),
        labels={**LABELS, **labels}
    )
    container.plotly_chart(fig, use_container_width=True)

def game_histogram(container, df, col, nbins=10, labels={}):
    fig = px.histogram(
        df,
        x=col,
        labels={**LABELS, **labels},
        nbins=nbins
    )
    fig.update_layout(bargap=0.30)
    container.plotly_chart(fig, use_container_width=True)

def collection_union_pie(container, base, existing, subsets):
    
    subset_intersect = MySet(functools.reduce(lambda a, b: a & b, subsets))
    subset_intersect.name = "Irisan semua"
    base_missing = MySet(base - existing)
    base_missing.name = "Tidak ditemukan"
    es = [existing] + subsets
    subset_exclusive_exist = [
        MySet(s.intersection(functools.reduce(
            lambda a, b: a - b, 
            [s1 for s1 in [
                s2 for s2 in es if s2 is not s
            ]]
        )))
        for s in subsets 
    ]
    for i in range(len(subsets)):
        subset_exclusive_exist[i].name = "Hanya {0}".format(subsets[i].name)
    
    data = [subset_intersect, *subset_exclusive_exist, base_missing]
    data = [(s.name, len(s)) for s in data]

    df = pd.DataFrame(data, columns=["Kelompok", "Jumlah"])

    simple_pie(container, df)

def collection_union_pie_2(container, df, appids, exclude=[]):
    appids = {k: v for k, v in appids.items() if k not in exclude}
    subsets = []
    for k, v in appids.items():
        v = MySet({int(x) for x in v})
        v.name = k
        subsets.append(v)
    union = MySet(functools.reduce(lambda a, b: a | b, subsets))
    union.name = "Union"
    existing = MySet({int(x) for x in df["steam_appid"]})
    existing.name = "Exists"

    collection_union_pie(
        container,
        union,
        existing,
        subsets
    )


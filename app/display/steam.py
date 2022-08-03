import streamlit as st
import pandas as pd
from ..global_data import Constants
import plotly.express as px
from numerize import numerize
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
from ..functions.util import sorted_keys, groupby_tag, group_others, join_tag, MySet
import functools
from ..functions.steam import LABELS

def show_metrics(container, series, metric_type=1):
    if metric_type==1:
        col1, col2, col3 = container.columns(3)
        col1.metric("Median", numerize.numerize(series.median()))
        col2.metric("Mean", numerize.numerize(series.mean()))
        col3.metric("Max", numerize.numerize(series.max()))

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
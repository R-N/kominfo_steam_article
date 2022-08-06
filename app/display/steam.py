import streamlit as st
import pandas as pd
from ..global_data import Constants
import plotly.express as px
import plotly.graph_objects as go
from numerize import numerize
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
from ..functions.util import sorted_keys, groupby_tag, group_others, join_tag, MySet
import functools
from ..functions.steam import LABELS
from ..display.util import fig_defaults

def show_metrics(container, series, metric_type=1, compact=False):
    series = series.astype(float)
    if metric_type==1:
        col1, col2, col3, col4, col5 = container.columns(5) if not compact else ([container] * 5)
        col1.metric("Median", numerize.numerize(series.median()))
        col2.metric("Mean", numerize.numerize(series.mean()))
        col3.metric("Max", numerize.numerize(series.max()))
        col4.metric("Sum", numerize.numerize(series.sum()))
        col5.metric("Count", numerize.numerize(float(series.count())))
    if metric_type==2:
        col1, col2, col3 = container.columns(3) if not compact else ([container] * 3)
        col1.metric("Median", numerize.numerize(series.median()))
        col2.metric("Mean", numerize.numerize(series.mean()))
        col3.metric("Max", numerize.numerize(series.max()))

def show_metrics_table(container, series, metric_type=1):
    series = series.astype(float)
    if metric_type==1:
        values = {
            "Median": numerize.numerize(series.median()),
            "Mean": numerize.numerize(series.mean()),
            "Max": numerize.numerize(series.max()),
            "Sum": numerize.numerize(series.sum()),
            "Count": numerize.numerize(float(series.count()))
        }
    if metric_type==2:
        values = {
            "Median": numerize.numerize(series.median()),
            "Mean": numerize.numerize(series.mean()),
            "Max": numerize.numerize(series.max())
        }
    df = pd.DataFrame.from_dict([values])
    container.dataframe(df)

def simple_pie(container, df, values="Jumlah", names="Kelompok", labels={}):
    
    fig = px.pie(
        df, 
        values=values, 
        names=names,
        labels={**LABELS, **labels}
    )
    fig_defaults(fig)
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

def game_scatter(container, df, x, y, zs, hlines=[], labels={}):
    zs = [
        pd.Series([numerize.numerize(float(x)) for x in df[z].to_numpy()], name=z) 
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
    fig_defaults(fig)
    if isinstance(hlines, list):
        for hline in hlines:
            if isinstance(hline, pd.Series):
                hline = hline[y]
            fig.add_hline(y=hline, line_dash="dash", line_color="red")
    if isinstance(hlines, dict):
        xmin, xmax = df[x].min(), df[x].max()
        for name, hline in hlines.items():
            if isinstance(hline, pd.Series):
                hline = hline[y]
            fig.add_trace(
                go.Scatter(
                    x=[xmin, xmax], 
                    y=[hline, hline],
                    mode='lines', 
                    line=dict(dash='dash'),
                    name=name
                )
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
    fig_defaults(fig)
    container.plotly_chart(fig, use_container_width=True)

def game_bar_horizontal(container, df, x, y, y_list=True, hover_data=[], aggfunc=lambda x: x.sum(), labels={}, agg=False):
    y_list = y_list and y is not None
    if y_list:
        if agg:
            df = aggfunc(groupby_tag(
                df,
                y
            )).sort_values(x, ascending=True)
            sorting = df
            y = None
            #sorting = aggfunc(groupby_tag(df[[x, y]], y))
        else:
            df = join_tag(
                df,
                y
            ).sort_values(x, ascending=True)
            sorting = aggfunc(groupby_tag(df[[x, y]], y))
    elif y is not None:
        sorting = aggfunc(df.groupby(y))
    else:
        sorting = df
    sorting = sorting.sort_values(x, ascending=True)
    fig = px.bar(
        df, 
        x=x, 
        y=y, 
        #color=df2.index, 
        orientation='h',
        hover_data=[x] if not agg else [x, *hover_data],
        category_orders=sorting.index.to_list(),
        labels={**LABELS, **labels}
    )
    fig_defaults(fig)
    container.plotly_chart(fig, use_container_width=True)

def game_histogram(container, df, col, nbins=10, height=450, labels={}):
    fig = px.histogram(
        df,
        x=col,
        labels={**LABELS, **labels},
        nbins=nbins,
        height=height
    )
    fig.update_layout(
        bargap=0.30,
        margin=dict(l=20, r=20, t=20, b=20)
    )
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


st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id})
def limit_df(
    container, 
    df_paid, 
    col, 
    default=None,
    key="default", 
    compact=False
):
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
        100.0 * 10**3: "< 100 ribu",
        50.0 * 10**3: "< 50 ribu",
        20.0 * 10**3: "< 20 ribu",
        10.0 * 10**3: "< 10 ribu",
        5.0 * 10**3: "< 5 ribu",
        2.0 * 10**3: "< 2 ribu",
        1.0 * 10**3: "< 1000",
        500: "< 500",
        200: "< 200",
        100: "< 100",
        50: "< 50",
        20: "< 20",
        10: "< 10",
        "custom": "Custom"
    }
    min_value_limit = min_value
    min_value_limit = df_paid[df_paid[col] > 0.0][col].min()
    limit_labels = {
        k: v for k, v in limit_labels.items() 
        if not isinstance(k, (int, float)) or (min_value_limit <= k and k <= max_value)
    }
    labels = [None, *sorted_keys(
        limit_labels, 
        condition=lambda x: isinstance(x, (int, float)), 
        reverse=True
    ), "custom"]
    try:
        index = labels.index(default)
    except ValueError:
        index = 0
    col1, col2 = container.columns(2) if not compact else ([container] * 2)
    limit = col1.selectbox(
        "Batas",
        labels, 
        format_func=lambda x: limit_labels[x],
        index=index,
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
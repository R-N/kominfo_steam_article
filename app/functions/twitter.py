import streamlit as st
import pandas as pd
from ..global_data import Constants
import requests

DEFAULT_MIN_SENTIMENT_SCORE = 0.0

API = "recent"
QUERIES=[
    "kominfo pse",
    "kominfo blokir",
    "kominfo block",
    "kominfo steam",
    "kominfo paypal",
    "kominfo epic",
    "kominfo facebook",
    "kominfo whatsapp",
    "kominfo instagram",
    "kominfo google",
    "kominfo bom",
    "kominfo serang",
    "kominfo",
    "#BlokirKominfo"
]
DATES = [
    "2022-07-26",
    "2022-07-27",
    "2022-07-28",
    "2022-07-29",
    "2022-07-30",
    "2022-07-31"
]
SENTIMENT_LABELS = {
    "positive": "Positif",
    "neutral": "Netral",
    "negative": "Negatif"
}
POLARITY_LABEL_COLS = ["negative", "neutral", "positive"]
POLARITY_LABEL_VOLUME_COLS = ["{0}_volume".format(k) for k in POLARITY_LABEL_COLS]

EXCLUDE_QUERIES = [
    "kominfo judi",
    "kominfo bom",
    "kominfo serang",
    "kominfo slot"
]
INCLUDE_QUERIES = [k for k in QUERIES if k not in EXCLUDE_QUERIES]
DEFAULT_QUERIES = [
    "kominfo",
    "kominfo block",
    "kominfo blokir",
    "kominfo pse",
    "kominfo steam",
    "#BlokirKominfo"
]
LABELS = {
    "date": "Tanggal",
    "variable": "Variabel",
    "all": "Semua",
    "like_count": "Like",
    "reply_count": "Reply",
    "retweet_count": "Retweet",
    "quote_count": "Quote",
    "engagement": "Interaksi",
    "count": "Jumlah",
    "count_rt": "Jumlah (termasuk retweet)",
    "count_rt_quote": "Jumlah (termasuk retweet dan quote)",
    **SENTIMENT_LABELS,
    **{
        "{0}_volume".format(k): "{0} (volume)".format(v)
        for k, v in SENTIMENT_LABELS.items()
    },
    **{
        "{0}_no_neutral".format(k): "{0} (tanpa netral)".format(v)
        for k, v in SENTIMENT_LABELS.items()
        if "neutral" not in k
    },
    **{
        "{0}_volume_no_neutral".format(k): "{0} (volume, tanpa netral)".format(v)
        for k, v in SENTIMENT_LABELS.items()
        if "neutral" not in k
    }
}

def build_file_name(api, query, date, format="csv"):
    file_name = "search_{0}_{1}_{2}.{3}".format(
        api,
        query,
        date,
        format
    )
    return file_name

st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id})
def load_df(excel_path):
    if excel_path.endswith("csv"):
        df = pd.read_csv(excel_path)
    else:
        df = pd.read_excel(excel_path, sheet_name="data")
    return df

st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id})
def prepare_df(df):
    df = df.copy()
    if "Unnamed: 0" in df.columns:
        df = df.drop(["Unnamed: 0"], axis=1)
    df = df.set_index('id')
    df["lang"] = df["lang"].replace("in", "id")
    df["volume"] = df[["like_count", "retweet_count"]].max(axis=1) + 1
    df["engagement"] = df[[
        "like_count", 
        "retweet_count",
        "quote_count",
        "reply_count"
    ]].max(axis=1)
    return df


st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id})
def load_all():
    all_data = {}
    for query in QUERIES:
        for date in DATES:
            file_name = build_file_name(API, query, date)
            excel_path = Constants.sentiment_folder + file_name
            try:
                df = load_df(excel_path)
                df = prepare_df(df)
                all_data[(query, date)] = df
            except FileNotFoundError:
                all_data[(query, date)] = None

    return all_data

st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id})
def aggregate_sentiment(df):
    count_sentiment = len(df)
    volume_sentiment = df["volume"].sum()
    sentiment_label_exists = list(df["sentiment_label"].unique())
    sentiment_label_count = df["sentiment_label"].value_counts()
    sentiment_label_volume = df[["sentiment_label", "volume"]].groupby("sentiment_label")["volume"].sum()
    
    return {
        "count_sentiment": count_sentiment,
        "volume_sentiment": volume_sentiment,
        **{
            k: sentiment_label_count[k]
            for k in sentiment_label_exists
        },
        **{
            "{0}_volume".format(k): sentiment_label_volume[k]
            for k in sentiment_label_exists
        }
    }

SENTIMENT_COLS = [
    "count_sentiment", "volume_sentiment", 
    "mean_polarity", "volume_polarity",
    *list(SENTIMENT_LABELS.keys()),
    *["{0}_volume".format(k) for k in SENTIMENT_LABELS.keys()]
]
st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id})
def aggregate_data(all_data, min_sentiment_score=DEFAULT_MIN_SENTIMENT_SCORE):
    aggregate = []
    for query in QUERIES:
        for date in DATES:
            key = (query, date)
            if key in all_data and all_data[key] is not None:
                df = all_data[key]
                count = len(df)
                count_rt = count + df["retweet_count"].sum()
                count_rt_quote = count_rt + df["quote_count"].sum()
                engagement_1 = count + df["engagement"].sum()
                df_sentiment = df[df["sentiment_score"] >= min_sentiment_score]
                sentiment_aggregate = aggregate_sentiment(df_sentiment)

                aggregate.append({
                    "id": build_file_name(API, query, date),
                    "api": API,
                    "query": query,
                    "date": date,
                    "count": count,
                    "count_rt": count_rt,
                    "count_rt_quote": count_rt_quote,
                    "engagement_1": engagement_1,
                    **sentiment_aggregate
                })
            else:
                aggregate.append({
                    "id": build_file_name(API, query, date),
                    "api": API,
                    "query": query,
                    "date": date,
                    "count": 0,
                })

    df = pd.DataFrame.from_dict(aggregate)
    df = df.set_index("id")
    """
    fillna_cols = [
        "count", "count_rt", "count_rt_quote", "engagement_1",
        *SENTIMENT_COLS,
        *["{0}_no_neutral".format(k) for k in SENTIMENT_COLS if "neutral" not in k]
    ]
    """
    df.fillna(0, inplace=True)
    return df

def filter_query(df, query):
    return df[df["query"]==query].set_index("date")

st.cache(hash_funcs={list: id, dict: id, pd.DataFrame: id})
def merge_data(all_data, queries, dates):
    merged = [all_data[(query, date)] for query in queries for date in dates]
    merged = pd.concat(merged)
    merged = merged[~merged.index.duplicated(keep='last')]
    return merged
    

@st.cache()
def get_tweet(id, fallback=None):
    try:
        api = 'https://publish.twitter.com/oembed?url=https://twitter.com/twitter/status/'+str(id)
        response = requests.get(api)
        return response.json()["html"]
    except:
        return fallback
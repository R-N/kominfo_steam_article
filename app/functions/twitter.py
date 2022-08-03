import streamlit as st
import pandas as pd
from ..global_data import Constants

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

def group_sentiment(df, bins=(-1.0/3.0, 1.0/3.0)):
    df["sentiment_label"] = pd.cut(
        x=df['polarity'],
        bins=[-1.0, *bins, 1.0],
        labels=list(SENTIMENT_LABELS.values())
    )
    return df

@st.cache()
def load_df(excel_path):
    if excel_path.endswith("csv"):
        df = pd.read_csv(excel_path)
    else:
        df = pd.read_excel(excel_path, sheet_name="data")
    return df

def prepare_df(df, sentiment_bins=(-1.0/3.0, 1.0/3.0)):
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
    df = group_sentiment(df, bins=sentiment_bins)
    return df

def load_all(sentiment_bins=(-1.0/3.0, 1.0/3.0)):
    all_data = {}
    for query in QUERIES:
        for date in DATES:
            file_name = build_file_name(API, query, date)
            excel_path = Constants.sentiment_folder + file_name
            try:
                df = load_df(excel_path)
                df = prepare_df(df, sentiment_bins=sentiment_bins)
                all_data[(query, date)] = df
            except FileNotFoundError:
                all_data[(query, date)] = None

    return all_data

def aggregate_sentiment(df):
    count_sentiment = len(df)
    volume_sentiment = df["volume"].sum()
    mean_polarity = df["polarity"].mean()
    volume_polarity = (df["polarity"] * df["volume"]).sum() / volume_sentiment
    sentiment_label_exists = list(df["sentiment_label"].unique())
    sentiment_label_count = df["sentiment_label"].value_counts()
    sentiment_label_volume = df[["sentiment_label", "volume"]].groupby("sentiment_label")["volume"].sum()
    
    return {
        "count_sentiment": count_sentiment,
        "volume_sentiment": volume_sentiment,
        "mean_polarity": mean_polarity,
        "volume_polarity": volume_polarity,
        **{
            k: sentiment_label_count[v]
            for k, v in SENTIMENT_LABELS.items()
            if v in sentiment_label_exists
        },
        **{
            "{0}_volume".format(k): sentiment_label_volume[v]
            for k, v in SENTIMENT_LABELS.items()
            if v in sentiment_label_exists
        }
    }

SENTIMENT_COLS = [
    "count_sentiment", "volume_sentiment", 
    "mean_polarity", "volume_polarity",
    *list(SENTIMENT_LABELS.keys()),
    *["{0}_volume".format(k) for k in SENTIMENT_LABELS.keys()]
]
def aggregate_data(all_data, min_subjectivity=0.5):
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
                df_sentiment = df[~df["polarity"].isna() & df["subjectivity"] >= min_subjectivity]
                sentiment_aggregate = aggregate_sentiment(df_sentiment)
                df_sentiment_no_neutral = df_sentiment[df_sentiment["sentiment_label"]!=SENTIMENT_LABELS["neutral"]]
                sentiment_aggregate_no_neutral = aggregate_sentiment(df_sentiment_no_neutral)

                aggregate.append({
                    "id": build_file_name(API, query, date),
                    "api": API,
                    "query": query,
                    "date": date,
                    "count": count,
                    "count_rt": count_rt,
                    "count_rt_quote": count_rt_quote,
                    "engagement_1": engagement_1,
                    **sentiment_aggregate,
                    **{
                        "{0}_no_neutral".format(k): v
                        for k, v in sentiment_aggregate_no_neutral.items()
                        if "neutral" not in k
                    }
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
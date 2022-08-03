import gc
import pandas as pd
import streamlit as st
from io import BytesIO

class Constants:
    data_folder = "data/"
    steam_path = data_folder + "steam_games_indo.xlsx"
    steam_appid_path = data_folder + "steam_appids.json"
    gtrends_path = data_folder + "gtrends.xlsx"
    counts_path = data_folder + "counts_recent_2022-07-25T17_00_00Z_2022-07-31T17_00_00Z.xlsx"
    trends_path = data_folder + "trends_Indonesia_2022-07-28T15_13_55Z_2022-07-31T05_51_56Z.xlsx"
    sentiment_folder = data_folder + "sentiment_csv/"

@st.cache(allow_output_mutation=True)
def init():

    _markdown = st.markdown
    def markdown_wrapper(x, *args, **kwargs):
        if isinstance(x, str):
            # return _markdown(x.replace(r"\n", r" \n"), *args, **kwargs)
            xs = x.split("\n")
            for x in xs:
                _markdown(x, *args, **kwargs)
        else:
            return _markdown(x, *args, **kwargs)
    st.markdown = markdown_wrapper

    _write = st.write
    def write_wrapper(x, *args, **kwargs):
        if isinstance(x, str):
            # return _write(x.replace(r"\n", r" \n"), *args, **kwargs)
            xs = x.split("\n")
            for x in xs:
                _write(x, *args, **kwargs)
        else:
            return _write(x, *args, **kwargs)
    st.write = write_wrapper
    
    pd.options.plotting.backend = "plotly"


def get_excel(df, sheet_name="Sheet 1"):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_csv(df):
    return df.to_csv(index=False).encode('utf-8')

import streamlit as st
import pandas as pd
from ..global_data import Constants
import plotly.express as px
from numerize import numerize
from ..functions.util import join_tag, groupby_tag, MySet
from ..display.util import selectbox_2, multiselect_2
from ..functions.steam import CSV_COLS, LABELS, COUNTRIES
from ..functions.steam import split_by_availability, init_df, merge_df
from ..pages.steam import game_availability_section, grouped_estimated_revenue_section
import json
import functools

def app():
    with open(Constants.steam_appid_path) as f:
        steam_appids = json.load(f)
    dfs = [
        init_df(pd.read_csv(Constants.steam_folder + k + ".csv"), country=k)
        for k in COUNTRIES.keys()
    ]
    df = merge_df(dfs)
    df_paid, df_free, df_unavailable, df_unreleased = split_by_availability(df)

    st.markdown("# Estimasi Penjualan")
    grouped_estimated_revenue_section(
        st,
        df_paid,
        labels={
            None: "Tanpa pengelompokan",
            "developers": "Developer",
            "publishers": "Publisher",
            "country": "Negara"
        },
        default="country"
    )
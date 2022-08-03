import streamlit as st

from app.global_data import init
from app.pages import home, steam, twitter, gtrends

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

page_dict = {}
page_names = []

def add_page(title, func):
    page_names.append(title)
    page_dict[title] = func


def run():
    # Drodown to select the page to run
    page_name = st.sidebar.selectbox(
        'App Navigation',
        page_names
    )

    # run the app function
    page_dict[page_name]()


init()

# Title of the main page
# st.title("Covid Forecasting Joint Learning")

# Add all your applications (pages) here
add_page("Home", home.app)
add_page("Steam", steam.app)
add_page("Twitter", twitter.app)
add_page("Google Trends", gtrends.app)

# The main app
run()

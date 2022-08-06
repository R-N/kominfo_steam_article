import streamlit as st

from app.global_data import init
from app.pages import home, steam, twitter, gtrends

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

def local_css(path):
    with open(path) as f:
        s = f.read().replace("\n", " ").rstrip()
    st.write(f'<style>{s}</style>', unsafe_allow_html=True)

def local_js(path):
    with open(path) as f:
        s = f.read().replace("\n", " ").rstrip()
    st.write(f'<script>{s}</script>', unsafe_allow_html=True)

def remote_css(url):
    st.write(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)    

def remote_js(url):
    st.write(f'<script src="{url}"></script>', unsafe_allow_html=True)   


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

#local_css("assets/css/bootstrap-4-utilities.min.css")
#local_css("assets/css/bootstrap.css")
local_css("assets/css/style.css")
# The main app
run()

#local_js("assets/js/jquery.slim.min.js")
#local_js("assets/js/popper.min.js")
#local_js("assets/js/bootstrap.min.js")
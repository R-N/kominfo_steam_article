import streamlit as st
import pandas as pd

def app():
    st.markdown("# Judul")
    st.markdown("Aaaa.")
    abstract_expander = st.expander(label='Abstract', expanded=True)
    with abstract_expander:
        st.markdown("## Abstract")
        st.markdown("")
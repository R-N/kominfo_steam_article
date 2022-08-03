import pandas as pd
import streamlit as st
from ..functions.util import sorted_keys


def selectbox_2(container, label, options, key="default", default=None):
    option_keys = sorted_keys(options)
    index=option_keys.index(default)
    index = index if index >= 0 else 0
    return container.selectbox(
        label,
        option_keys, 
        format_func=lambda x: options[x],
        index=index,
        key=key
    )
    

def multiselect_2(container, label, options, key="default", default=None):
    option_keys = sorted_keys(options)
    if isinstance(default, (list, tuple)):
        default = [d for d in default if d in options]
    return container.multiselect(
        label,
        option_keys, 
        format_func=lambda x: options[x],
        default=default,
        key=key
    )


def whitelist_plotly_vars(fig, whitelist):
    fig.for_each_trace(
        lambda trace: trace.update(visible="legendonly") 
            if trace.name not in whitelist else ()
    )
    return fig

def hide_plotly_vars(fig, blacklist):
    fig.for_each_trace(
        lambda trace: trace.update(visible="legendonly") 
            if trace.name in blacklist else ()
    )
    return fig

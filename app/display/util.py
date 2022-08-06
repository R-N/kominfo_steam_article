import pandas as pd
import streamlit as st
from ..functions.util import sorted_keys

def fig_defaults(fig):
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20)
    )

def selectbox_2(container, label, options, key="default", default=None):
    option_keys = sorted_keys(options)
    count = len(option_keys)
    if count == 0:
        return default
    elif count == 1:
        return option_keys[0]
    try:
        index = option_keys.index(default)
    except ValueError:
        index = 0
    return container.selectbox(
        label,
        option_keys, 
        format_func=lambda x: options[x],
        index=index,
        key=key
    )
    

def multiselect_2(container, label, options, key="default", default=None):
    option_keys = sorted_keys(options)
    count = len(option_keys)
    if count == 0:
        return []
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

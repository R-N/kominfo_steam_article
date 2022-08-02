import pandas as pd
import streamlit as st

def sorted_keys(dict, condition=lambda x: True, reverse=False):
    return list(sorted([
        x for x in dict.keys() if condition(x)
    ], reverse=reverse))
    
    

def join_tag(df, col, include_na=True):
    if col is None:
        return df
    if include_na:
        df[col] = df[col].fillna("<NA>")
    else:
        df = df.loc[~df[col].isna()]
    tag = pd.DataFrame(df[col].tolist(), index=df.index).stack()
    tag.index = tag.index.droplevel(-1)
    tag.name = col
    # tag = tag.drop_duplicates()
    return df.drop(col, axis=1).join(tag)

def groupby_tag(df, col, include_na=True):
    if col is None:
        return df
    return join_tag(df, col, include_na=include_na).groupby(col)

def group_others(others, others_name="Others", list_cols=[]):
    index = ",".join(others.index.to_numpy())
    others = others.sum().to_frame().T
    for c in [c for c in list_cols if c in others.columns]:
        others.at[0, c] = list(set(others.at[0, c]))
    index = others_name
    others["index"] = [index]
    others.set_index("index", inplace=True)
    return others


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

class MySet(set):
    def __init__(self, s=(), name=None):
        super(MySet,self).__init__(s)
        if name is None and hasattr(s, 'name'):
            name = s.name
        self.name = name



    @classmethod
    def _wrap_methods(cls, names):
        def wrap_method_closure(name):
            def inner(self, *args):
                result = getattr(super(cls, self), name)(*args)
                if isinstance(result, set) and not hasattr(result, 'name'):
                    result = cls(result, name=self.name)
                return result
            inner.fn_name = name
            setattr(cls, name, inner)
        for name in names:
            wrap_method_closure(name)

MySet._wrap_methods(['__ror__', 'difference_update', '__isub__', 
    'symmetric_difference', '__rsub__', '__and__', '__rand__', 'intersection',
    'difference', '__iand__', 'union', '__ixor__', 
    'symmetric_difference_update', '__or__', 'copy', '__rxor__',
    'intersection_update', '__xor__', '__ior__', '__sub__',
])

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

def remove_duplicate_by_index(df):
    return df[~df.index.duplicated(keep='first')]

class Batch:
    def __init__(self, max_char=14000):
        self.max_char = max_char
        self.batch = []
        self.len = 0

    def add(self, text):
        length = len(text)
        if length + self.len > self.max_char:
            return False
        self.batch.append(text)
        self.len += length
        return True

class Batches:
    def __init__(self, max_char=14000):
        self.max_char = max_char
        self.batches = [Batch(max_char=max_char)]

    @property
    def last_batch(self):
        return self.batches[-1]

    def new_batch(self):
        self.batches.append(Batch(max_char=self.max_char))

    def add(self, text):
        if not self.last_batch.add(text):
            self.new_batch()
            self.add(text)

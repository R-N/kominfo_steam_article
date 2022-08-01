import pandas as pd

def sorted_keys(dict, condition=lambda x: True, reverse=False):
    return list(sorted([
        x for x in dict.keys() if condition(x)
    ], reverse=reverse))
    

def groupby_tag(df, col, include_na=True):
    if col is None:
        return df
    if include_na:
        df[col] = df[col].fillna("<NA>")
    else:
        df = df.loc[~df[col].isna()]
    tag = pd.DataFrame(df[col].tolist()).stack()
    tag.index = tag.index.droplevel(-1)
    tag.name = 'tag'
    tag = tag.drop_duplicates()
    df_grouped = df.join(tag).groupby('tag')
    return df_grouped

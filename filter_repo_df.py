import numpy as np
import streamlit as st

@st.experimental_memo
def filter_repo_df(df,cols,
            filt_option,sort_option,
            filt_val,sort_direction,
            sort_algo='',filt_algo='',
            **kwargs):
    if df[filt_option].dtype=='datetime64[ns]':
        print('yes')
        df = df.loc[df[filt_option] > np.datetime64(filt_val),cols]\
                .sort_values(sort_option, ascending=sort_direction,)

    else:
        df = df.loc[df[filt_option] > filt_val,cols]\
                .sort_values(sort_option, ascending=sort_direction,)

    return df
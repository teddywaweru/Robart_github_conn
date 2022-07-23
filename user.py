from PIL import Image
from io import BytesIO
import streamlit as st
import pandas as pd
from request_data import get_data, get_data_async
from wrapper_func import measure_time
import requests
from time import time
import numpy as np


@measure_time
def show_user_details(
        user: dict, user_df: pd.DataFrame()
        ) -> None:

    user_repos_df = pd.DataFrame(user['repos'])

    user_repos_df[['created_at','updated_at','pushed_at']] = \
        user_repos_df[['created_at','updated_at','pushed_at']].astype('datetime64')
    # user_repos_df[['created_at','updated_at','pushed_at']] = \
        # pd.to_datetime(user_repos_df[['created_at','updated_at','pushed_at']]) \
        #     .dt.strftime('%Y-%m-%d T%I:%M:%SZ')

    col1, col2,col3 = st.columns([1.5,4,2])

    # Dictinoary of Numeric colummns that can be used in sorting
    FILT_COLS_DICT = {
        'Size': 'size', 'Watchers': 'watchers_count', 'Forks': 'forks_count',
        'Open Issues': 'open_issues_count', 
    }
    SORT_COLS_DICT = {
        'Updated Date':'updated_at', 'Created Date':'created_at',
        'Pushed Date':'pushed_at'

    }
    SORT_COLS_DICT.update(FILT_COLS_DICT)

    with col1:
        st.image(user['avatar'], width=100)
        st.text(f"Number of Public \nrepos:\t {user_df.loc[0,'public_repos']}")
        st.write(f"Bio:")
        st.write(f"{user_df.loc[0,'bio']}")

    with col2:

        st.multiselect(
            'Select additional columns to display.',
            options=user_repos_df.columns
        )
        st.write(f"{user['name']}'s Repositories:")

        # stargazers = get_data_async(user_repos_df['stargazers_url'])
        
        # stargazers_count = [len(i) for i in stargazers]
        # print(stargazers_count)

        filt_option = st.selectbox('Filter Repositories by:',options=SORT_COLS_DICT.keys())

        if filt_option:
            max_val = user_repos_df[SORT_COLS_DICT[filt_option]].max()
            if max_val == 0:
                st.info(f'{user["name"]} does not have any {filt_option} for any the public repositories.')
                st.slider(label=f'To limit number of repos by {filt_option}',
                        disabled=True)
                st.dataframe(user_repos_df)
 
            else:
                if user_repos_df[SORT_COLS_DICT[filt_option]].dtype != 'int64':
                    filt_val = st.date_input('Dated before',
                        pd.Timestamp(user_repos_df[SORT_COLS_DICT[filt_option]].min()))

                else:
                    filt_val = st.slider(label=f'To limit number of repos by {filt_option}',
                                min_value=0,max_value=max_val)



    with col3:
        st.write('')
        st.write('')
        st.write('')
        st.write('Sort by:')
        sort_options = SORT_COLS_DICT.keys()
        sort_option = st.selectbox('Options',sort_options)

        sort_radio = st.radio('Sort direction:', options=['Ascending','Descending'])
        sort_direction = True if sort_radio=='Ascending' else False

    col1, col2 = st.columns([1.5,6])
    with col1:
        x = 3 if 4==5 else 9 
        pass
    with col2:
        cols = ['id', SORT_COLS_DICT[filt_option], SORT_COLS_DICT[sort_option]]
        if SORT_COLS_DICT[filt_option] == SORT_COLS_DICT[sort_option]:
            cols.pop(-1)
        cols.extend(
            [
                col for col in 
                ['name','created_at', 'updated_at', 'pushed_at',
                'forks_count','stargazers_count',]
                if col not in ['id', SORT_COLS_DICT[filt_option], SORT_COLS_DICT[sort_option]]
            ]
        )
        print(cols)
        if user_repos_df[SORT_COLS_DICT[filt_option]].dtype=='datetime64[ns]':
            st.dataframe(
                user_repos_df.loc[user_repos_df[SORT_COLS_DICT[filt_option]] > np.datetime64(filt_val),cols]
                    .sort_values(SORT_COLS_DICT[sort_option], ascending=sort_direction,kind='mergesort')
            )
        else:
            st.dataframe(
                user_repos_df.loc[user_repos_df[SORT_COLS_DICT[filt_option]] > filt_val,cols]
                    .sort_values(SORT_COLS_DICT[sort_option], ascending=sort_direction,kind='mergesort')
            )
        # print(user_repos_df['updated_at'].dtype)
        # print(user_repos_df.columns)

    """repo data columns:
    id, name, description, fork, fork_url, languages_url, created_at, updated_at, pushed_at, 
    """

from PIL import Image
from io import BytesIO
import streamlit as st
import pandas as pd
from request_data import get_data
from wrapper_func import measure_time
import requests
from time import time


class User:

    @measure_time
    def __init__(self,row):

        with requests.Session() as session:

            av_time_start = time()
            user_avatar = session.get(row['avatar_url'])
            av_time_end = time()

            repo_time_start = time()
            self.user_repos = session.get((row['repos_url']))
            repo_time_end = time()

        print(f'Avatar - REPOS Start time:{repo_time_start-av_time_start}')
        print(f'Avatar - REPOS End time:{repo_time_end-av_time_end}')
        print(f'Avatar time:{av_time_end-av_time_start}')
        print(f'repo time:{repo_time_end-repo_time_start}')

        self.user = row['login']
        self.name = row['name']
        self.user_avatar = Image.open(BytesIO(user_avatar.content))


@measure_time
def show_user_details(user: User) -> None:

    col1, col2,col3 = st.columns([1,4,2])
    user_repos_df = pd.DataFrame(user.user_repos.json()) 

    with col1:
        st.image(user.user_avatar, width=100)
        st.write(f'Count of repos: {len(user.user_repos.json())}')

    with col2:
        st.write(f"{user.name}'s Repositories:")
        
        filt_options = [
            col for col in user_repos_df.columns
        ]
        filt_option = st.selectbox('Filter Repositories by:',options=filt_options)

        if filt_option in ['stargazers_url']:
            h = st.slider('Limit Number of Users:',min_value=2,max_value=10)
        st.dataframe(user_repos_df)
        st.write(user_repos_df.columns)

    with col3:
        st.write('Sort by:')
        sort_options = [col for col in user_repos_df.columns]
        st.selectbox('Options',sort_options)


    """repo data columns:
    id, name, description, fork, fork_url, languages_url, created_at, updated_at, pushed_at, 
    """

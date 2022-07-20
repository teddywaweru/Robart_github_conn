from PIL import Image
from io import BytesIO
import streamlit as st
import pandas as pd
from request_data import get_data



class User:
    def __init__(self,row):
        self.user = row['login']

        user_avatar = get_data(row['avatar_url'])
        self.user_avatar = Image.open(BytesIO(user_avatar.content))

        self.user_url = get_data(row['url'])

        self.user_html_url = get_data(row['html_url'])

        self.user_repos = get_data((row['repos_url']))


def show_user_details(user: User):

    col1, col2,col3 = st.columns([1,4,2])

    with col1:
        st.image(user.user_avatar, width=100)
        st.write(f'Count of repos: {len(user.user_repos.json())}')

    with col2:
        user_repos_df = pd.DataFrame(user.user_repos.json()) 
        st.dataframe(user_repos_df)
        st.write(user_repos_df.columns)

    with col3:
        st.write('Sort by:')
        sort_options = [col for col in user_repos_df]
        st.selectbox('Options',sort_options)

        st.write('Filter by:')

    """repo data columns:
    id, name, description, fork, fork_url, languages_url, created_at, updated_at, pushed_at, 
    """

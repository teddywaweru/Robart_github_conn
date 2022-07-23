import os
import requests
import streamlit as st
from PIL import Image
from io import BytesIO
from wrapper_func import measure_time



# AUTH_TOKEN = st.secrets['GITHUB_USER']
GITHUB_USERNAME = st.secrets['GITHUB_USER']
GITHUB_TOKEN = st.secrets['GITHUB_TOKEN']
AUTH_TOKEN = (GITHUB_USERNAME,GITHUB_TOKEN)


def get_data(
        url: str, page: int=1
        ) -> requests.models.Response():
    """_summary_

    :param _type_ url: _description_
    :return _type_: _description_
    """    
    
    res = requests.get(f"{url}?page={page}&per_page=100", auth=AUTH_TOKEN)
    #pages are statically set to have 100 values per request(maximum value)

    return res

@st.experimental_memo
def get_avatar(url):
    avatar = get_data(url).content
    return Image.open(BytesIO(avatar))

@st.experimental_memo
def get_data_async(urls):
    results = []
    with requests.Session() as session:
        session.auth = AUTH_TOKEN
        for url in urls:
            results.append(session.get(url).json())
    return results

@measure_time
@st.experimental_memo
def get_all_repos(row):
    responses = []
    pages = row['public_repos'] //100       #pages are statically set to have 100 values per request
    
    for page in range(1,pages+2):
        res = get_data(url=row['repos_url'],page=page).json()
        responses.extend(res)
    return responses

@measure_time
@st.experimental_memo
def save_user_data(row):
    user = {
        'user': row['login'],
        'name': row['name'],
        'avatar': get_avatar(row['avatar_url']),
        'repos': get_all_repos(row),     #requires additional work: users have varying number of repos
    }
    if user['name'] == None:
        user['name'] = row['login']
    return user


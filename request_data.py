import os
import requests
import streamlit as st

# AUTH_TOKEN = st.secrets['GITHUB_USER']
GITHUB_USERNAME = st.secrets['GITHUB_USER']
GITHUB_TOKEN = st.secrets['GITHUB_TOKEN']
AUTH_TOKEN = (GITHUB_USERNAME,GITHUB_TOKEN)

def get_data(url) -> requests.models.Response():
    """_summary_

    :param _type_ url: _description_
    :return _type_: _description_
    """    
    res = requests.get(url, auth=AUTH_TOKEN)
    return res

import os
import time
import requests
import streamlit as st
from PIL import Image
from io import BytesIO
from wrapper_func import measure_time
import aiohttp
import asyncio

import nest_asyncio



# AUTH_TOKEN = st.secrets['GITHUB_USER']
GITHUB_USERNAME = st.secrets['GITHUB_USER']
GITHUB_TOKEN = st.secrets['GITHUB_TOKEN']
AUTH_TOKEN = (GITHUB_USERNAME,GITHUB_TOKEN)
global CONN,RESPONSES

@st.experimental_memo(show_spinner=False)
def get_data(
        url: str, page: int=1
        ) -> requests.models.Response:
    """_summary_

    :param _type_ url: _description_
    :return _type_: _description_
    """    
    res = requests.get(f"{url}?page={page}&per_page=100", auth=AUTH_TOKEN)
    #pages are statically set to have 100 values per request(maximum value)

    return res

@st.experimental_memo(show_spinner=False)
def get_avatar(url) -> Image:
    avatar = get_data(url).content
    return Image.open(BytesIO(avatar))


# @st.experimental_memo
async def get_data_async(urls,parallel_requests):

    semaphore = asyncio.Semaphore(parallel_requests)
    CONN = aiohttp.TCPConnector(limit_per_host=100,limit=0,ttl_dns_cache=300)

    session = aiohttp.ClientSession(connector=CONN)

    async def get(url):
        RESPONSES = []
        async with semaphore:
            async with session.get(url=url,ssl=False,
            auth=aiohttp.BasicAuth(AUTH_TOKEN)) as response:
                obj = json.loads(await response.read())
                RESPONSES.append(obj)
            return RESPONSES
    val = await asyncio.gather(*(get(url) for url in urls))
    await session.close()

    CONN.close()
    return val



# @measure_time
# @st.experimental_memo
# def get_all_repos(row):

@measure_time
@st.experimental_memo(show_spinner=False)
def save_user_data(row):
    user = {
        'user': row['login'],
        'name': row['name'],
        'avatar': get_avatar(row['avatar_url']),
        'user_html': row['url']
    }
    if user['name'] == None:
        user['name'] = row['login']

    # RESPONSES = []
    pages = row['public_repos'] //100       #pages are statically set to have 100 values per request

    RESPONSES = []
    for page in range(1,pages+2):
        with st.spinner(
            text=f"""
            API call may take up to {(pages + 1)*2.5} seconds
            Fetching page {page} of {pages+1}.
            """):
            res = get_data(url=row['repos_url'],page=page).json()
            RESPONSES.extend(res)
    user['repos'] = RESPONSES    
    # print(f'{len(RESPONSES)}------------------')
    # print(f'------------------{pages}')


    return user


@measure_time
async def save_user_data_async(row):
    user = {
        'user': row['login'],
        'name': row['name'],
        'avatar': get_avatar(row['avatar_url']),
        'user_html': row['url']
    }
    if user['name'] == None:
        user['name'] = row['login']

    # RESPONSES = []
    pages = row['public_repos'] //100       #pages are statically set to have 100 values per request

    RESPONSES = []
    #if-else intended to enable segmenting for typical & concurrent requests 
    if pages > -1:
        for page in range(1,pages+2):
            res = get_data(url=row['repos_url'],page=page).json()
            RESPONSES.extend(res)
        user['repos'] = RESPONSES    
        print(f'{len(RESPONSES)}------------------')
        print(f'------------------{pages}')

    else:
        #initiates concurrent request calls
        urls = [f"{row['repos_url']}?page={page}&per_page=100" for page in range(1,pages+2)]
        loop = asyncio.new_event_loop()

        nest_asyncio.apply()

        asyncio.set_event_loop(loop=loop)
        # asyncio.set_event_loop(loop)
        val = loop.run_until_complete(get_data_async(urls, 1))
        

        user['repos'] =  *val[0][0],     #requires additional work: users have varying number of repos
        # print(user['repos'])

    return user


def get_api_header() -> requests.models.Response.json:
    res = requests.get('https://api.github.com/rate_limit',auth=AUTH_TOKEN)
    print(res.headers)
    return res.json()

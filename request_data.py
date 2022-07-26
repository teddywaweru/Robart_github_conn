import os
import requests
import streamlit as st
from PIL import Image
from io import BytesIO
from wrapper_func import measure_time
import aiohttp
import asyncio
import json



# AUTH_TOKEN = st.secrets['GITHUB_USER']
GITHUB_USERNAME = st.secrets['GITHUB_USER']
GITHUB_TOKEN = st.secrets['GITHUB_TOKEN']
AUTH_TOKEN = (GITHUB_USERNAME,GITHUB_TOKEN)
RESPONSES = []
global CONN

@st.experimental_memo
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

@st.experimental_memo
def get_avatar(url) -> Image:
    avatar = get_data(url).content
    return Image.open(BytesIO(avatar))


@st.experimental_memo
async def get_data_async(urls,parallel_requests):

    semaphore = asyncio.Semaphore(parallel_requests)
    session = aiohttp.ClientSession(connector=CONN)

    async def get(url):
        async with semaphore:
            async with session.get(url=url,ssl=False,
            auth=aiohttp.BasicAuth(AUTH_TOKEN)) as response:
                obj = json.loads(await response.read())
                RESPONSES.append(obj)
    await asyncio.gather(*(get(url) for url in urls))
    await session.close()



# @measure_time
# @st.experimental_memo
# def get_all_repos(row):

@measure_time
# @st.experimental_memo
async def save_user_data(row):
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
    if pages < 5:
        for page in range(1,pages+2):
            res = get_data(url=row['repos_url'],page=page).json()
            RESPONSES.extend(res)
        user['repos'] = RESPONSES    
        print(f'{len(RESPONSES)}------------------')
        print(f'------------------{pages}')
    else:
        urls = [f"{row['repos_url']}?page={page}&per_page=100" for page in range(1,pages+1)]
        # loop = asyncio.get_event_loop()
        # asyncio.set_event_loop(loop)
        # loop.run_until_complete(get_data_async(urls, pages))
        CONN = aiohttp.TCPConnector(limit_per_host=100,limit=0,ttl_dns_cache=300)
        asyncio.run(get_data_async(urls, pages))

        CONN.close()
        print(f'{len(RESPONSES)}------------------')

        user['repos'] =  RESPONSES,     #requires additional work: users have varying number of repos


    return user



import os
import requests
import streamlit as st
import aiohttp
import asyncio

conn = aiohttp.TCPConnector(limit=None,ttl_dns_cache=300)
session = aiohttp.ClientSession(connector=conn)
results = []
conc_req = 40

async def gather_with_conc(n,*tasks):
    sem = asyncio.Semaphore(n)

    async def sem_task(task):
        async with sem:
            return await task

        return await asyncio.gather(*(sem_task(task)for task in tasks))

async def get_async(url,session,results):
    async with session.get(url) as response:
        obj = await response.json()
        results.append(obj)
         


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

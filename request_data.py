import os
import requests


GITHUB_USERNAME = os.environ['GITHUB_LOGIN']
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
AUTH_TOKEN = (GITHUB_USERNAME,GITHUB_TOKEN)

def get_data(url) -> requests.models.Response():
    """_summary_

    :param _type_ url: _description_
    :return _type_: _description_
    """    
    res = requests.get(url, auth=AUTH_TOKEN)
    return res

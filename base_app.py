import streamlit as st
from st_aggrid import AgGrid
import pandas as pd
import traceback
from pathlib import Path
import asyncio
from PIL import Image
from io import BytesIO
from user import show_user_details
from request_data import get_data, save_user_data
from custom_exceptions import ExcessUsersException
from wrapper_func import measure_time


st.set_page_config(
    layout='wide'
)

st.sidebar.write('')




@measure_time
def load_markdown_file(path):
    """Load markdown docs

    :param str path: path to markdown doc
    :return str: Markdown text
    """        
    return Path(path).read_text()

st.title('Hello World')
# with open('markdowns\intro.md') as f:
st.markdown(load_markdown_file('markdowns/intro.md'))


@measure_time
@st.experimental_memo()
def init_get_data() -> pd.DataFrame():
    res = get_data('https://api.github.com/users')
    print(res.headers)
    res = res.json()
    df = pd.DataFrame(res)
    return df.loc[:4,:]


@measure_time
@st.experimental_memo
def get_user_data(user) -> pd.DataFrame():
    
    if user:
        try:
            res = get_data(f'https://api.github.com/users/{user}')
            user_data = res.json()
            print(res.headers)
            user_data = pd.DataFrame([user_data])
            return user_data
        except:
            traceback.print_exc()
    else:
        return init_get_data()


search_user = st.text_input(
    label='Username to search',
    placeholder='Enter username ie. teddywaweru, microsoft',
)

def start_page():
    user_df = get_user_data(search_user)
    #if no user was found from the search, the DF has 'message' in its columns
    if 'message' in user_df.columns:
        st.write('User not found in the Github system. Please search again.')

    #if no user was searched for, DF would be similar to the initial dataset.
    elif user_df.shape == init_get_data().shape:
        st.write("""No search output to display...yet.
        Showing default users provided by the Github API.""")

    #if search was successful
    else:
        st.write('Search Successful')



    # user_ = user_df.apply(lambda x: user_profile(x),axis=1)

    res = get_data('https://api.github.com/rate_limit')
    print(res.headers)


    try:

        st.dataframe(
            # user_df[['login','name','node_id','html_url','repos_url','url']]
            user_df
            )

        print(len(get_data(user_df.loc[0,'repos_url']).json()))
        if user_df.shape[0] != 1:   #Only one user should be in the data
            raise ExcessUsersException

        show_user_details(save_user_data(user_df.iloc[0]),user_df)
        
    except (KeyError,ExcessUsersException):
        traceback.print_exc()
        st.dataframe(user_df)



    # AgGrid(load_data(search_user))



    # Introduction: base data, input points,
    # Data preview, analysis, sorting
    # Concept of relying on utilizing a dataset over OOP
    # Clor schemes
    # Implement dict rather than class

if __name__ == '__main__':
    start_page()
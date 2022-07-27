"""This is the starting point of the application
The script loads the initial view for the user. & 
provides a search input.
"""
import traceback
from pathlib import Path
import asyncio
import streamlit as st
import pandas as pd
from user import show_user_details
from request_data import get_data
from custom_exceptions import ExcessUsersException, NoUserException
from wrapper_func import measure_time


# Set page Configuration
st.set_page_config(
    layout='wide'
)


@measure_time
def load_markdown_file(path) -> str:
    """Load Markdown docs

    :param str path: path string
    :return str: String of loaded document
    """
    with open(Path(path),'r',encoding='utf-8') as md_f:
        return md_f.read()



@measure_time
@st.experimental_memo(show_spinner=False)
def init_get_data() -> pd.DataFrame():
    """load initial user data from Github API

    :return Pandas Dataframe: DataFrame of users
    """
    res = get_data('https://api.github.com/users')
    print(res.headers)
    res = res.json()
    init_df = pd.DataFrame(res)
    return init_df.loc[:4,:]


@measure_time
@st.experimental_memo(show_spinner=False)
def get_user_data(user) -> pd.DataFrame():
    """Search for user on Github API using username

    :param str user: username
    :return pandas DataFrame: user's details DataFrame, or initial DataFrame
    """
    if user:
        try:
            res = get_data(f'https://api.github.com/users/{user}')
            user_data = res.json()
            user_data = pd.DataFrame([user_data])
            return user_data
        except:
            traceback.print_exc()
    else:
        return init_get_data()



async def start_page() -> None:
    st.title('Hello World')
    st.markdown(load_markdown_file('markdowns/intro.md'))

    col1, col2 = st.columns([3,4])
    with col1:
        search_user = st.text_input(
            label='Username to search',
            placeholder='Enter username ie. teddywaweru, microsoft',
    )

    with col2:
        pass
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
        st.info('Search Successful!')


    try:
        if 'name' not in user_df.columns:
            raise NoUserException
        
        st.dataframe(
            user_df[['login','name','node_id','html_url','repos_url','url']]
            )

        if user_df.shape[0] > 1:
            #default data has more than one column
            raise NoUserException

        if user_df.shape[0] != 1:   #Only one user should be in the data
            raise ExcessUsersException

        show_user_details(user_df)

    except KeyError:
        st.dataframe(user_df)
        traceback.print_exc()

    except ExcessUsersException:
        st.dataframe(user_df)
        traceback.print_exc()

    except NoUserException:
        st.dataframe(user_df)
        traceback.print_exc()

    except:
        traceback.print_exc()

def main():
    """Main function
    """    
    print('---------------restarting-----------')
    asyncio.run(start_page())
    print('---------------done-----------------')



#Starting point for the application
if __name__ == '__main__':
    main()



#Pending TODO 's
#Introduction✅
#Search Capability✅
    #Concurrent Searching
#Filtering✅
    #Different Searching algorithms
# Sorting✅
    #Different Sorting algorithms
# Showing repo statistics✅
#Displaying X-rate limit calls✅
#Code refactoring & distribution✅
#Comments
#Color schemes❌Not functioning
#Input point for User's GITHUB_TOKEN & GITHUB_USER❌Not feasible


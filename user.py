from PIL import Image
from io import BytesIO
from time import time
from datetime import datetime
import requests
import streamlit as st
import pandas as pd
from request_data import get_data, get_data_async, get_api_header
from wrapper_func import measure_time
import numpy as np
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
from filter_repo_df import filter_repo_df
from plotly import graph_objects as go



@measure_time
def show_user_details(
        user: dict, user_df: pd.DataFrame()
        ) -> None:
    start = time()
    user_repos_df = pd.DataFrame(user['repos'])

    user_repos_df[['created_at','updated_at','pushed_at']] = \
        user_repos_df[['created_at','updated_at','pushed_at']].astype('datetime64')
    user_df['created_at'] = user_df['created_at'].astype('datetime64')
    # user_repos_df[['created_at','updated_at','pushed_at']] = \
        # pd.to_datetime(user_repos_df[['created_at','updated_at','pushed_at']]) \
        #     .dt.strftime('%Y-%m-%d T%I:%M:%SZ')

    print(f'1------{time()-start}')
    # Dictinoary of Numeric colummns that can be used in sorting
    SORT_FILT_COLS_DICT = {
        'Updated Date':'updated_at', 'Created Date':'created_at',
        'Pushed Date':'pushed_at','Size': 'size',
        'Watchers': 'watchers_count', 'Forks': 'forks_count',
        'Open Issues': 'open_issues_count', 
    }


    st.markdown(f"### {user['name']}'s Profile:")

    col1, col2 = st.columns([1,5])

    with col1:
        st.image(user['avatar'], width=200)
    
    with col2:
        st.text(f"Created on: \t\t{user_df.loc[0,'created_at']}")
        st.text(f"Location: \t\t{user_df.loc[0,'location']}")
        st.text(f"Company: \t\t{user_df.loc[0,'company']}")
        st.text(f"Count of Public repos: \t{user_df.loc[0,'public_repos']}")
        st.text(f"Bio: \t{user_df.loc[0,'bio']}")
    st.write('')


    col1, col2,_,col3 = st.columns([2,2,2,2])

    print(f'2------{time()-start}')
    with col1:
        st.markdown('#### Repository Data')
        
        filt_option = st.selectbox('Filter Repositories by:',options=SORT_FILT_COLS_DICT.keys())

        if filt_option:
            max_val = user_repos_df[SORT_FILT_COLS_DICT[filt_option]].max()
            if max_val == 0:
                st.info(f'{user["name"]} does not have any {filt_option} for any the public repositories.')
                st.slider(label=f'To limit number of repos by {filt_option}',
                        disabled=True)
                filt_val = 0
                # st.dataframe(user_repos_df)
 
            else:
                if user_repos_df[SORT_FILT_COLS_DICT[filt_option]].dtype != 'int64':
                    filt_val = st.date_input('Dated before',
                        pd.Timestamp(user_repos_df[SORT_FILT_COLS_DICT[filt_option]].min()))

                else:
                    max_val = np.int64(max_val).item()
                    filt_val = st.slider(label=f'To limit number of repos by {filt_option}',
                                min_value=0,max_value=max_val)
    with col2:
        st.markdown('#### :')
        # st.write('')
        # st.write('')
        sort_options = SORT_FILT_COLS_DICT.keys()
        sort_option = st.selectbox('Sort Repositories by:',sort_options)

        sort_radio = st.radio('Sort direction:', options=['Ascending','Descending'])
        sort_direction = True if sort_radio=='Ascending' else False



    print(f'3------{time()-start}')
    with col3:
        pass


    col1, col2 = st.columns([6,4])


    with col1:

        cols = ['id', SORT_FILT_COLS_DICT[filt_option], SORT_FILT_COLS_DICT[sort_option]]
        if SORT_FILT_COLS_DICT[filt_option] == SORT_FILT_COLS_DICT[sort_option]:
            cols.pop(-1)
        cols.extend(
            [
                col for col in 
                ['name','created_at', 'updated_at', 'pushed_at',
                'forks_count','stargazers_count',]
                if col not in ['id', SORT_FILT_COLS_DICT[filt_option], SORT_FILT_COLS_DICT[sort_option]]
            ]
        )
        # print(user_repos_df.columns)

        df = filter_repo_df(df=user_repos_df,cols=cols,
                    filt_option=SORT_FILT_COLS_DICT[filt_option],
                    sort_option=SORT_FILT_COLS_DICT[filt_option],
                    filt_val=filt_val,sort_direction=sort_direction)


        gb = GridOptionsBuilder().from_dataframe((df))
        gb.configure_selection(selection_mode='single',)
        gridOptions = gb.build()

        grid_response = AgGrid(df,gridOptions=gridOptions,
                        # data_return_mode='AS_INPUT',
                        theme='streamlit',reload_data=True,
                        update_mode='SELECTION_CHANGED',
                        )

        print(f'4------{time()-start}')
        x=False
        if st.checkbox(
            label='Download Data?'
        ):
            st.download_button(
                label='Download dataframe',data=user_repos_df.to_csv().encode('utf-8'),
                file_name=f"{user['name'].replace(' ','_')}_repositories.csv"
            )

        if len(grid_response['selected_rows']) == 0:
            selected = df.iloc[0]
        else:    
            selected = grid_response['selected_rows'][0]


        selected_repo = user_repos_df.loc[user_repos_df['id']==selected['id'],:]\
                            .iloc[0]
                    
        print(f'5------{time()-start}')
    with col2:
    #Name, html_url,description,fork,created_at,updated_at,pushed_at,sie,forks,open_issues,watchers,languages_url
        st.markdown(f"#### {selected_repo['name']} Repository Details")
        st.write(f"Repository name: {selected_repo['name']}")
        st.write(f"URL [Link]({selected_repo['html_url']})")
        languages = get_data(selected_repo['languages_url']).json()

        if len(languages)==0:
            st.info('No distribution of languages available for this repository.')
        else:
            fig = go.Figure()
            fig.add_trace(
                go.Pie(
                    labels=list(languages.keys()),
                    values=list(languages.values()),
                )
            )
            fig.update_layout(
                width=300,height=200,
                margin=dict(l=0,r=0,b=25,t=0),
                title={'text':"Distribution of Languages",
                    'y':0.05,
                    'yanchor':'bottom'}
            )
            st.plotly_chart(fig)

    api_header = get_api_header()
    # print('------------------')
    # print(api_header['resources']['core'])
    # print(api_header['resources']['core']['used'])
    # print(api_header['resources']['core']['remaining'])
    # print('------------------')
    print(api_header)
    print(f'6------{time()-start}')

    with col3:
        st.metric(
                label="API calls remaining:",
            value=f"""{api_header['resources']['core']['remaining']}
                        / {api_header['resources']['core']['limit']}""" ,
            # delta=value-10,
        )
        print(f'')

        st.metric(
                label="Next Reset:",
            value=f"{datetime.fromtimestamp(api_header['resources']['core']['reset'])}",
            # delta=value-10,
        )

    """repo data columns:
    id, name, description, fork, fork_url, languages_url, created_at, updated_at, pushed_at, 
    """

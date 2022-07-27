"""
Loads all user content to view.
"""

import time
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import GridOptionsBuilder, AgGrid
from plotly import graph_objects as go
from filter_repos import filter_repo_df
from request_data import get_data, save_user_data,get_api_header
from wrapper_func import measure_time



@measure_time
def show_user_details(user_df: pd.DataFrame) -> None:
    start = time.time()
    user = save_user_data(user_df.iloc[0])
    user_repos_df = pd.DataFrame(user['repos'])

    user_repos_df[['created_at','updated_at','pushed_at']] = \
        user_repos_df[['created_at','updated_at','pushed_at']].astype('datetime64')
    user_df['created_at'] = user_df['created_at'].astype('datetime64')


    # Dictinoary of Numeric colummns that can be used in sorting
    SORT_FILT_COLS_DICT = {
        'Size': 'size','Updated Date':'updated_at',
        'Created Date':'created_at', 'Pushed Date':'pushed_at',
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

        sort_options = SORT_FILT_COLS_DICT.keys()
        sort_option = st.selectbox('Sort Repositories by:',sort_options)

        sort_radio = st.radio('Sort direction:', options=['Ascending','Descending'])
        sort_direction = True if sort_radio=='Ascending' else False


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
                if col not in
                [
                    'id', SORT_FILT_COLS_DICT[filt_option],
                    SORT_FILT_COLS_DICT[sort_option]
                ]
            ]
        )

        df = filter_repo_df(df=user_repos_df,cols=cols,
                    filt_option=SORT_FILT_COLS_DICT[filt_option],
                    sort_option=SORT_FILT_COLS_DICT[sort_option],
                    filt_val=filt_val,sort_direction=sort_direction)


        grid_builder = GridOptionsBuilder().from_dataframe((df))
        grid_builder.configure_selection(selection_mode='single',)
        grid_options = grid_builder.build()

        grid_response = AgGrid(df,gridOptions=grid_options,
                        data_return_mode='AS_INPUT',
                        theme='streamlit',reload_data=True,
                        update_mode='SELECTION_CHANGED',
                        )

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
                    
    with col2:

        st.markdown(f"#### {selected_repo['name']} Repository Details")
        st.write(f"Repository name: {selected_repo['name']}")
        st.write(f"Repository [URL Link]({selected_repo['html_url']})")
        st.text(f"""Created:\t \tLast Update:\t\tSize: \n{selected_repo['created_at']}\t{selected_repo['updated_at']}\t{selected_repo['size']}""")
        languages = get_data(selected_repo['languages_url']).json()

        if len(languages)==0:
            st.info('No distribution of languages available for this repository.')
        else:
            fig = go.Figure()
            fig.add_trace(
                go.Pie(
                    labels=list(languages.keys()),
                    values=list(languages.values()),
                    textposition='inside'
                )
            )
            fig.update_layout(
                width=300,height=200,
                margin=dict(l=0,r=0,b=25,t=0),
                title={'text':"Distribution of Languages",
                    'y':0.05,
                    'yanchor':'bottom'},
                uniformtext_minsize=12,
                uniformtext_mode='hide'
            )
            st.plotly_chart(fig)

    api_header = get_api_header()

    print(api_header)

    with col3:
        st.metric(
                label="API calls remaining:",
            value=f"""{api_header['resources']['core']['remaining']}
                        / {api_header['resources']['core']['limit']}""" ,
        )

        st.metric(
                label="Next Reset:",
            value=f"{datetime.fromtimestamp(api_header['resources']['core']['reset'])}",
        )

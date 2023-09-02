from data.fetch_data import fetch_pdf_info
import pandas as pd

def get_tkr_list(my_etf_tkr):

    pdf_info = fetch_pdf_info(etf_tkr=my_etf_tkr)

    pdf_df = pd.DataFrame(pdf_info)

    tkr_list = pdf_df.sort_values(by="float_shares", ascending=False).head().reset_index(drop=True)['child_stk_tkr'].to_list()

    return tkr_list

import json

def get_news_dict_list(*args, **kwargs):

    etf_tkr = kwargs.pop('etf_tkr', 'AIQ')
        
    with open(f'./etf_news_infos/{etf_tkr}.json', 'r') as file:
        data = json.load(file)

    return data

def get_llm_answer(*args, **kwargs):

    etf_tkr = kwargs.pop('etf_tkr', 'AIQ')
        
    with open(f'./etf_llm_summary/{etf_tkr}.json', 'r') as file:
        data = json.load(file)

    return data

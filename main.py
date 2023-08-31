from fastapi import FastAPI

from core.gpt_semantic_search import get_vectordb, get_filter, get_similar_symbols

from core.financial_filtering import get_lowest_PBR_stks, get_momentums

from core.get_common_issues import get_news_dict_list

from starlette.middleware.cors import CORSMiddleware
import uvicorn

origins = ["*"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import json

@app.get("/stk_filtering")
def get_stk_filtering(etf_tkr: str = "AIQ"):
    
    vectordb = get_vectordb()
    
    filter_list = get_filter(etf_tkr=etf_tkr)
    
    with open(f'etf_subcategory_infos/{etf_tkr}.json', 'r') as f:
        
        json_data = json.load(f)
        
    for i, subcateogry in enumerate(json_data['subcategory_lists']):
        
        keyword = subcateogry["description"]
        
        similar_stk_list = get_similar_symbols(
            vectordb=vectordb,
            keyword=keyword,
            filter_list=filter_list,
            k=5,
        )
        
        subcateogry['stk_list'] = similar_stk_list
        
        json_data['subcategory_lists'][i] = subcateogry
        
    
    
    docs_list = vectordb.get(where={'$or': filter_list})

    lowest_PBR_stks_tuple_list = get_lowest_PBR_stks(docs_list=docs_list)
    
    value_dict = {
        "title": "잠재가치 높은",
        "description": "내재 가치 대비 저평가되어 있는 기업들입니다."
    }
    
    value_dict["stk_list"] = [s[1] for s in lowest_PBR_stks_tuple_list]
        
    
    
    momentum_dict = {
        "title": "꾸준히 우상향 하는",
        "description": "모멘텀 좋은 기업들입니다."
    }
    
    momentum_tuple_list = get_momentums(filter_list=filter_list)
    
    momentum_dict["stk_list"] = [s[1] for s in momentum_tuple_list]
    
    
    json_data['financial_filtering_lists'] = [value_dict, momentum_dict]
        
    return json_data

from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessage, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
import os


@app.get('/common_issues')
def get_common_issues(etf_tkr: str = "AIQ"):

    with open('conf.json', 'r') as f:
        json_data = json.load(f)
    
    os.environ['OPENAI_API_KEY'] = json_data['API_KEY']

    news_data = str(get_news_dict_list(etf_tkr=etf_tkr))

    template = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content=(
                    # "You are now acting as an intelligent fund manager who is fluent in both English and Korean. I will provide you with news headlines for 8 different stock tickers. Your task is to identify the common themes or keywords that appear across all these different tickers, not just within each individual one. Please summarize these overarching themes in Korean, in a coherent format limited to 10 sentences. Ensure your response is tailored to be informative for stock investors and is presented in a professional manner."
                    "You are now acting as an intelligent fund manager fluent in both English and Korean. I will provide you with news headlines of different stock tickers. Your task is to identify common themes that appear across all these different tickers, not just within each individual one. Please summarize these overarching themes in Korean, in a coherent format limited to 10 sentences. Ensure your response is tailored to be informative for stock investors and is presented in a professional manner. Additionally, please conclude your answer with a noun. don't answer in bullet points"
                )
            ),
            HumanMessagePromptTemplate.from_template("{text}"),
        ]
    )

    llm = ChatOpenAI(model="gpt-3.5-turbo")
    
    ret = llm(template.format_messages(text=news_data))

    return ret


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
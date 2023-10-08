import logging
from uvicorn.config import LOGGING_CONFIG, Config
import json
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from core.gpt_semantic_search import get_vectordb, get_filter, get_similar_symbols

from core.financial_filtering import get_lowest_PBR_stks, get_momentums

from core.get_common_issues import get_news_dict_list, get_llm_answer

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


@app.get('/.well-known/pki-validation/E3A1B108EB8EA884704FFBE17DBC29F4.txt')
def get_pki_test():
    file_name = "E3A1B108EB8EA884704FFBE17DBC29F4.txt"

    file_path = f"./{file_name}"

    file = open(file_path, "r")

    return PlainTextResponse(file.read())


@app.get("/stk_filtering")
def get_stk_filtering(etf_tkr: str = "AIQ"):

    vectordb = get_vectordb()

    filter_list = get_filter(etf_tkr=etf_tkr)

    with open(f'etf_subcategory_infos/{etf_tkr}.json', 'r') as f:

        json_data = json.load(f)

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


@app.get('/common_issues')
def get_common_issues(etf_tkr: str = "AIQ"):
    return get_llm_answer(etf_tkr=etf_tkr)


if __name__ == "__main__":

    config = Config("main:app", host="0.0.0.0")
    server = uvicorn.Server(config=config)
    server.run()

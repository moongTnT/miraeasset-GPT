from fastapi import FastAPI

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

import json

@app.get("/stk_filtering")
def get_stk_filtering(etf_tkr: str = "AIQ"):
    
    vectordb = get_vectordb()
    
    filter_list = get_filter(etf_tkr=etf_tkr)
    
    with open(f'etf_subcategory_infos/{etf_tkr}.json', 'r') as f:
        
        json_data = json.load(f)
        
    # for i, subcateogry in enumerate(json_data['subcategory_lists']):
        
    #     keyword = subcateogry["description"]
        
    #     #  여기서 병목 현상 걸리는 이슈 발생
    #     similar_stk_list = get_similar_symbols( 
    #         vectordb=vectordb,
    #         keyword=keyword,
    #         filter_list=filter_list,
    #         k=5,
    #     )
        
    #     subcateogry['stk_list'] = similar_stk_list
        
    #     json_data['subcategory_lists'][i] = subcateogry
        
    
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


from uvicorn.config import LOGGING_CONFIG, Config
import uvicorn
import logging

if __name__ == "__main__":
    DATE_FMT = "%Y-%m-%d %H:%M:%S"

    # Modify uvicorn's access logging format
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s [%(levelname)s] [%(filename)s] [%(process)d] %(client_addr)s - "%(request_line)s" %(status_code)s'
    LOGGING_CONFIG["formatters"]["access"]["datefmt"] = DATE_FMT
    
    # Modify uvicorn's default logging format
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(levelname)s] [%(filename)s] - %(message)s"
    LOGGING_CONFIG["formatters"]["default"]["datefmt"] = DATE_FMT

    # Create a new file handler for access logs and add it to uvicorn's logger
    file_handler_access = logging.FileHandler("access.log")
    file_handler_access.setFormatter(logging.Formatter(
        LOGGING_CONFIG["formatters"]["access"]["fmt"],
        DATE_FMT
    ))

    # Create a new file handler for default logs and add it to uvicorn's logger
    file_handler_default = logging.FileHandler("app.log")
    file_handler_default.setFormatter(logging.Formatter(
        LOGGING_CONFIG["formatters"]["default"]["fmt"],
        DATE_FMT
    ))

    # Add handlers to the LOGGING_CONFIG
    LOGGING_CONFIG["handlers"]["file_handler_access"] = {
        "class": "logging.FileHandler",
        "filename": "access.log",
        "formatter": "access"
    }
    LOGGING_CONFIG["handlers"]["file_handler_default"] = {
        "class": "logging.FileHandler",
        "filename": "app.log",
        "formatter": "default"
    }

    # Associate the handlers with the loggers
    LOGGING_CONFIG["loggers"]["uvicorn.access"]["handlers"].append("file_handler_access")
    LOGGING_CONFIG["loggers"]["uvicorn"]["handlers"].append("file_handler_default")

    print("logger setup")

    config = Config("main:app", host="0.0.0.0", log_config=LOGGING_CONFIG)
    server = uvicorn.Server(config=config)
    server.run()
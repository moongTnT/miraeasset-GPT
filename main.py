from fastapi import FastAPI
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

@app.get("/stk_filtering")
def get_stk_filtering(etf_tkr: str = "AIQ"):

    common_issues = {
        "title": "dummy_title",
        "content": "dummy_content"
    }

    unstructured_categories = [
        {
            "title": "세계 경제구조 변화로 수혜받는 '로보틱스' 산업",
            "describe": "세계적인 인구구조 변화 AI의 결합으로 다양한 분    야에서 활용도 상승",
            "stks": ["엔비디아", "애플", "TSMC", "AMD"]
        },
        {
            "title": "생성형 AI로 탄력 받은 인공지능 산업",
            "describe": "ChatGPT 등 생성형 AI가 일상으로 빠르게 침투하면서 AI발전 가속화",
            "stks": ["애플", "마이크로소프트", "구글", "아마존"]
        }
    ]

    structured_categories = [
        {
            "title": "모멘텀 좋은",
            "stks": ["엔비디아", "아마존"],
        },
        {
            "title": "안정성 높은",
            "stks": ["엔비디아", "아마존"],
        },
        {
            "title": "위험도 낮은",
            "stks": ["TSMC", "아마존"],
        },
    ]

    return {
        "common_issues": common_issues,
        "unstructured_categories": unstructured_categories,
        "structured_categories": structured_categories
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
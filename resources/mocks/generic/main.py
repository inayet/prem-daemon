import logging
import uuid
from datetime import datetime as dt

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


class ChatCompletionInput(BaseModel):
    model: str
    messages: list[dict]
    temperature: float = 1.0
    top_p: float = 1.0
    n: int = 1
    stream: bool = False
    stop: str | list | None = ""
    max_tokens: int = 7
    presence_penalty: float = 0.0
    frequence_penalty: float = 0.0
    logit_bias: dict | None = {}
    user: str = ""


class ChatCompletionResponse(BaseModel):
    id: str = uuid.uuid4()
    model: str
    object: str = "chat.completion"
    created: int = int(dt.now().timestamp())
    choices: list[dict]
    usage: dict = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


class EmbeddingsInput(BaseModel):
    model: str
    input: str
    user: str = ""


class EmbeddingObject(BaseModel):
    object: str = "embedding"
    index: int = 0
    embedding: list[float]


class EmbeddingUsage(BaseModel):
    prompt_tokens: int = 0
    total_tokens: int = 0


class EmbeddingsResponse(BaseModel):
    object: str = "list"
    data: list[EmbeddingObject]
    model: str = ""
    usage: EmbeddingUsage


class HealthResponse(BaseModel):
    status: bool


router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health():
    return HealthResponse(status=True)


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(body: ChatCompletionInput):
    return {
        "id": str(uuid.uuid4()),
        "model": "chat-mock",
        "object": "chat.completion",
        "created": int(dt.now().timestamp()),
        "choices": [
            {
                "role": "assistant",
                "index": idx,
                "message": {"role": "assistant", "content": text},
                "finish_reason": "stop",
            }
            for idx, text in enumerate(["Hello world"])
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


@router.post("/embeddings", response_model=EmbeddingsResponse)
async def embeddings(body: EmbeddingsInput):
    return EmbeddingsResponse(
        object="list",
        data=[EmbeddingObject(embedding=[0.1, 0.1, 0.1])],
        model=body.model,
        usage=EmbeddingUsage(),
    )


def get_application() -> FastAPI:
    application = FastAPI(title="prem-chat", debug=True, version="0.0.1")
    application.include_router(router, prefix="/api/v1")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return application


app = get_application()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

"""OLMo（画像を学習していないテキストのみのLLM）を使った会話アシスタントサービスの土台。

トラックD第1段階：モデルのロード・推論をサービス化するところまで。
ツール呼び出し（トラックB・Cとの結合）は素のOLMoでは不安定なこと（zero-shot実験、
docs/design/animation-creation-implementation-plan.md参照）が分かっているため、
ファインチューニング前提で別段階として扱う。CPU推論で十分な速度が出ることを
予備調査で確認済みのため、GPUは不要（motion-api・avatar-apiと異なりCPUで動く）。
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "allenai/OLMo-2-0425-1B-Instruct"

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"],
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    max_new_tokens: int = 200


@app.post("/chat")
def chat(req: ChatRequest):
    inputs = tokenizer.apply_chat_template(
        [m.model_dump() for m in req.messages], add_generation_prompt=True, return_tensors="pt", return_dict=True,
    )
    output = model.generate(**inputs, max_new_tokens=req.max_new_tokens)
    reply = tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return {"reply": reply}

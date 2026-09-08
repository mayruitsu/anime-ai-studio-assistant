"""OLMo（画像を学習していないテキストのみのLLM）を使った会話アシスタントサービス。

ツール呼び出しは素のOLMoではzero-shotだと不安定（精度10.6%）なため、
`finetune_olmo.py`でLoRAファインチューニングしたアダプタ（精度100.0%、
docs/tech/chat-api.md参照）を`CHAT_API_LORA_ADAPTER_DIR`で指定すれば読み込む。
未指定の場合は素のOLMoのまま動作する（開発・動作確認用）。
"""
import json
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from peft import PeftModel
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from tool_calling import dispatch_tool_call, parse_tool_call
from tools import format_tools_for_prompt

MODEL_NAME = "allenai/OLMo-2-0425-1B-Instruct"
TOOLS_API_BASE_URL = os.environ.get("CHAT_API_TOOLS_BASE_URL", "http://localhost:8080")
LORA_ADAPTER_DIR = os.environ.get("CHAT_API_LORA_ADAPTER_DIR")

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"],
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
if LORA_ADAPTER_DIR:
    model = PeftModel.from_pretrained(model, LORA_ADAPTER_DIR)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    max_new_tokens: int = 200


def generate_reply(messages: list[dict], max_new_tokens: int) -> str:
    inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt", return_dict=True)
    output = model.generate(**inputs, max_new_tokens=max_new_tokens)
    return tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)


@app.post("/chat")
def chat(req: ChatRequest):
    messages = [{"role": "system", "content": format_tools_for_prompt()}] + [m.model_dump() for m in req.messages]
    raw_reply = generate_reply(messages, req.max_new_tokens)

    tool_call = parse_tool_call(raw_reply)
    if tool_call is None:
        return {"reply": raw_reply, "tool_call": None}

    try:
        tool_result = dispatch_tool_call(tool_call, TOOLS_API_BASE_URL)
    except Exception as e:
        return {"reply": raw_reply, "tool_call": tool_call, "tool_error": str(e)}

    followup = messages + [
        {"role": "assistant", "content": raw_reply},
        {"role": "user", "content": f"ツール実行結果：{json.dumps(tool_result, ensure_ascii=False)}\n"
                                     "この結果を踏まえて、ユーザーへの返答を日本語で作成して。"},
    ]
    final_reply = generate_reply(followup, req.max_new_tokens)
    return {"reply": final_reply, "tool_call": tool_call, "tool_result": tool_result}

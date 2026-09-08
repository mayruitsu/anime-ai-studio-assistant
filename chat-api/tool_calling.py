"""会話モデルの出力からツール呼び出しを抜き出し、実行するための処理。"""
import json

import requests

from tools import TOOL_NAMES


def parse_tool_call(text: str) -> dict | None:
    """モデルの出力から`{"tool": ..., "params": {...}}`形式のJSONを抜き出す。

    小規模モデルは指示通りJSONのみを出力するとは限らないため、応答の前後に
    説明文が付いていても、該当する形式のJSONオブジェクトが含まれていれば拾う。
    """
    for start, ch in enumerate(text):
        if ch != "{":
            continue
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        data = json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        break
                    params = data.get("params", {}) if isinstance(data, dict) else None
                    if isinstance(data, dict) and data.get("tool") in TOOL_NAMES and isinstance(params, dict):
                        return {"tool": data["tool"], "params": params}
                    break
    return None


def dispatch_tool_call(tool_call: dict, api_base_url: str) -> dict:
    """トラックBの橋渡し（/tools/call）にツール呼び出しを送り、結果を返す。"""
    response = requests.post(f"{api_base_url}/tools/call", json=tool_call, timeout=65)
    response.raise_for_status()
    return response.json()["result"]

"""会話アシスタントが呼び出せるツールの定義。

`frontend/src/toolBridge.js`のcreateToolRegistry()で実際に実行される
ツール名・パラメータと一致させる必要がある。
"""

TOOLS = [
    {"name": "get_current_pose", "description": "現在のVRMの各ボーンの回転を取得する", "parameters": {}},
    {"name": "set_bone_rotation", "description": "指定したボーンの回転を設定する",
     "parameters": {"bone_name": "string", "x": "number", "y": "number", "z": "number"}},
    {"name": "add_keyframe", "description": "現在のポーズをキーフレームとして追加する", "parameters": {}},
    {"name": "clear_keyframes", "description": "記録したキーフレームをすべて削除する", "parameters": {}},
    {"name": "export_keyframe_video", "description": "記録したキーフレームから動画を書き出す", "parameters": {}},
    {"name": "load_vrm_model", "description": "指定したURLのVRMモデルを読み込む",
     "parameters": {"url": "string"}},
    {"name": "start_motion_generation", "description": "テキストからAIモーション生成を開始する（数分かかるためjob_idを返す）",
     "parameters": {"prompt": "string"}},
    {"name": "get_motion_generation_status", "description": "AIモーション生成の進捗状況を確認する",
     "parameters": {"job_id": "string"}},
    {"name": "play_and_export_generated_motion", "description": "生成済みのAIモーションを再生して動画を書き出す",
     "parameters": {"job_id": "string"}},
]

TOOL_NAMES = {tool["name"] for tool in TOOLS}


def format_tools_for_prompt() -> str:
    """システムプロンプトに埋め込む、ツール一覧の説明文を作る。"""
    lines = ["利用可能なツール一覧："]
    for tool in TOOLS:
        params = ", ".join(f"{k}: {v}" for k, v in tool["parameters"].items()) or "なし"
        lines.append(f"- {tool['name']}({params}): {tool['description']}")
    lines.append(
        "\nツールを呼び出したいときは、他の文章を含めず次の形式のJSONのみを出力すること：\n"
        '{"tool": "ツール名", "params": {パラメータ}}'
    )
    return "\n".join(lines)

"""tool_calling.pyの動作確認用スクリプト（parse_tool_callのみ、ネットワーク不要）。"""
from tool_calling import parse_tool_call


def main():
    exact = '{"tool": "add_keyframe", "params": {}}'
    assert parse_tool_call(exact) == {"tool": "add_keyframe", "params": {}}
    print("OK: 純粋なJSONを正しく解析")

    with_prose = 'はい、キーフレームを追加します。\n{"tool": "add_keyframe", "params": {}}\nよろしいですか？'
    assert parse_tool_call(with_prose) == {"tool": "add_keyframe", "params": {}}
    print("OK: 前後に説明文があっても解析できる")

    with_params = '{"tool": "set_bone_rotation", "params": {"bone_name": "head", "x": 0.1, "y": 0, "z": 0}}'
    result = parse_tool_call(with_params)
    assert result["tool"] == "set_bone_rotation" and result["params"]["bone_name"] == "head"
    print("OK: パラメータ付きツール呼び出しを正しく解析")

    assert parse_tool_call("こんにちは、今日はいい天気ですね") is None
    print("OK: ツール呼び出しを含まない文章ではNoneを返す")

    unknown_tool = '{"tool": "delete_everything", "params": {}}'
    assert parse_tool_call(unknown_tool) is None
    print("OK: 未知のツール名は無視する（ハルシネーション対策）")


if __name__ == "__main__":
    main()

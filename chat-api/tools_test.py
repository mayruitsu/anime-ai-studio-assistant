"""tools.pyの動作確認用スクリプト。"""
from tools import TOOL_NAMES, TOOLS, format_tools_for_prompt


def main():
    assert "set_bone_rotation" in TOOL_NAMES
    assert "get_current_pose" in TOOL_NAMES
    assert len(TOOLS) == len(TOOL_NAMES), "ツール名が重複している"
    print(f"OK: {len(TOOLS)}個のツールが定義されている")

    prompt = format_tools_for_prompt()
    for tool in TOOLS:
        assert tool["name"] in prompt, f"{tool['name']}がプロンプトに含まれていない"
    assert '"tool"' in prompt and '"params"' in prompt
    print("OK: format_tools_for_promptが全ツールと出力形式の指示を含む")


if __name__ == "__main__":
    main()

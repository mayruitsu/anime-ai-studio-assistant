"""generate_finetune_dataset.pyの動作確認用スクリプト。"""
import json

from generate_finetune_dataset import generate_examples
from tool_calling import parse_tool_call
from tools import TOOL_NAMES


def main():
    examples = generate_examples(seed=0)
    assert len(examples) > 50, f"生成件数が少なすぎる: {len(examples)}"
    print(f"OK: {len(examples)}件の対話データを生成")

    seen_tools = set()
    for example in examples:
        messages = example["messages"]
        assert [m["role"] for m in messages] == ["system", "user", "assistant"]
        assistant_text = messages[-1]["content"]
        # assistantの出力自体がparse_tool_callで正しく解析できることを確認
        # （学習データの正解ラベルが、実行時の解析ロジックと矛盾しないことの検証）
        parsed = parse_tool_call(assistant_text)
        assert parsed is not None, f"解析できないassistant出力: {assistant_text}"
        assert parsed["tool"] in TOOL_NAMES
        seen_tools.add(parsed["tool"])

    assert seen_tools == TOOL_NAMES, f"カバーされていないツールがある: {TOOL_NAMES - seen_tools}"
    print(f"OK: 全{len(TOOL_NAMES)}種類のツールが学習データでカバーされている")

    # 同じseedなら同じデータが再現されることを確認（学習の再現性のため）
    assert json.dumps(generate_examples(seed=0)) == json.dumps(examples)
    print("OK: 同じseedで再現可能")


if __name__ == "__main__":
    main()

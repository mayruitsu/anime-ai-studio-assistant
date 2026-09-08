"""ファインチューニング前後のツール呼び出し精度を、未学習のseedで生成した
held-outデータで比較する（骨格編集モデルの評価と同じ考え方）。
"""
import argparse

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from generate_finetune_dataset import generate_examples
from tool_calling import parse_tool_call

MODEL_NAME = "allenai/OLMo-2-0425-1B-Instruct"


def generate_reply(model, tokenizer, messages: list, device: str, max_new_tokens: int = 100) -> str:
    inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt", return_dict=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    output = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    return tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)


def evaluate(model, tokenizer, device: str, examples: list) -> float:
    correct = 0
    for example in examples:
        messages = example["messages"]
        expected = parse_tool_call(messages[-1]["content"])
        reply = generate_reply(model, tokenizer, messages[:-1], device)
        predicted = parse_tool_call(reply)
        if predicted == expected:
            correct += 1
    return correct / len(examples)


def main():
    parser = argparse.ArgumentParser(description="ファインチューニング前後のツール呼び出し精度を比較する")
    parser.add_argument("adapter_dir")
    parser.add_argument("--eval-seed", type=int, default=1, help="学習に使っていない未学習seed")
    args = parser.parse_args()

    device = "cuda"
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    base_model = AutoModelForCausalLM.from_pretrained(MODEL_NAME).to(device)
    eval_examples = generate_examples(seed=args.eval_seed)

    base_model.eval()
    with torch.no_grad():
        base_acc = evaluate(base_model, tokenizer, device, eval_examples)
    print(f"ファインチューニング前の精度: {base_acc:.1%}")

    tuned_model = PeftModel.from_pretrained(base_model, args.adapter_dir)
    tuned_model.eval()
    with torch.no_grad():
        tuned_acc = evaluate(tuned_model, tokenizer, device, eval_examples)
    print(f"ファインチューニング後の精度: {tuned_acc:.1%}")


if __name__ == "__main__":
    main()

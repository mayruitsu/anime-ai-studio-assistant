"""OLMoを、generate_finetune_dataset.pyで生成した対話データでLoRAファインチューニングする。

zero-shot実験でツール呼び出しが不安定と判明したため（docs/design/animation-creation-implementation-plan.md）、
LoRA（Low-Rank Adaptation、モデル全体ではなく小さな追加行列だけを学習する効率的な手法）で
ツール呼び出しの形式・判断を学習させる。学習データは全て自己生成の合成データのみを使用する。
"""
import argparse
import json
import random

import torch
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "allenai/OLMo-2-0425-1B-Instruct"


def load_dataset(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def encode_example(tokenizer, messages: list, device: str):
    """プロンプト部分（system+user）はloss計算対象外(-100)にし、assistantの
    応答部分のみを学習対象にする（instruction tuningの標準的なマスキング）。
    """
    prompt_ids = tokenizer.apply_chat_template(
        messages[:-1], add_generation_prompt=True, return_tensors="pt", return_dict=True)["input_ids"]
    full_ids = tokenizer.apply_chat_template(messages, return_tensors="pt", return_dict=True)["input_ids"]
    labels = full_ids.clone()
    labels[:, :prompt_ids.shape[1]] = -100
    return full_ids.to(device), labels.to(device)


def main():
    parser = argparse.ArgumentParser(description="OLMoをツール呼び出しデータでLoRAファインチューニングする")
    parser.add_argument("dataset_path")
    parser.add_argument("output_dir")
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--lora-rank", type=int, default=8)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    device = "cuda"
    random.seed(args.seed)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    base_model = AutoModelForCausalLM.from_pretrained(MODEL_NAME).to(device)
    lora_config = LoraConfig(r=args.lora_rank, lora_alpha=args.lora_rank * 2,
                              target_modules=["q_proj", "k_proj", "v_proj", "o_proj"], lora_dropout=0.05)
    model = get_peft_model(base_model, lora_config)
    model.print_trainable_parameters()

    examples = load_dataset(args.dataset_path)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)

    model.train()
    for epoch in range(args.epochs):
        random.shuffle(examples)
        total_loss = 0.0
        for example in examples:
            input_ids, labels = encode_example(tokenizer, example["messages"], device)
            loss = model(input_ids=input_ids, labels=labels).loss
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"epoch {epoch + 1}/{args.epochs}: avg loss={total_loss / len(examples):.4f}")

    model.save_pretrained(args.output_dir)
    print(f"LoRAアダプタを{args.output_dir}に保存しました")


if __name__ == "__main__":
    main()

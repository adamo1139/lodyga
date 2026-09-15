#!/usr/bin/env python3
"""Generate Łodyga answers through an OpenAI-compatible /completions API."""

import argparse
import json
import time
import tomllib
import urllib.request
from pathlib import Path


def load_tokenizer(cfg):
    from transformers import AutoTokenizer

    path = cfg["model"]["tokenizer"]
    subfolder = cfg["model"].get("tokenizer_subfolder")
    if subfolder:
        from huggingface_hub import snapshot_download

        path = Path(snapshot_download(path, allow_patterns=[f"{subfolder}/*"])) / subfolder
    return AutoTokenizer.from_pretrained(
        str(path), trust_remote_code=cfg["model"].get("trust_remote_code", False)
    )


def complete(cfg, prompt):
    api = cfg["api"]
    generation = dict(cfg.get("generation", {}))
    payload = {"model": api["model"], "prompt": prompt, **generation}
    payload.pop("base_url", None)
    payload.pop("api_key_env", None)
    body = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    key_name = api.get("api_key_env")
    if key_name:
        import os

        key = os.environ.get(key_name)
        if key:
            headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(api["base_url"].rstrip("/") + "/completions", body, headers)
    with urllib.request.urlopen(req, timeout=api.get("timeout", 600)) as response:
        result = json.load(response)
    return result["choices"][0]["text"]


def render(tokenizer, messages, enable_thinking=None):
    kwargs = {"tokenize": False, "add_generation_prompt": True}
    if enable_thinking is not None:
        kwargs["enable_thinking"] = enable_thinking
    return tokenizer.apply_chat_template(messages, **kwargs)


def clean_answer(text):
    """Keep server-returned text out of the next chat-template turn."""
    # /completions returns only the completion, but some servers include the
    # generated end-of-turn token when no stop sequence was configured.
    for marker in ("<|im_end|>", "<|eot_id|>", "<|end_of_turn|>"):
        if marker in text:
            text = text.split(marker, 1)[0]
    for marker in ("<|im_start|>assistant", "<|im_start|> assistant"):
        if text.lstrip().startswith(marker):
            text = text.lstrip()[len(marker):]
    return text.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--questions", type=Path, default=Path("data/mt_bench/question.jsonl"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()
    cfg = tomllib.loads(args.config.read_text())
    model_id = cfg["model"]["id"]
    output = args.output or Path("data/mt_bench/model_answer") / f"{model_id}.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    tokenizer = load_tokenizer(cfg)
    existing = {}
    if output.exists() and not args.no_resume:
        for line in output.read_text().splitlines():
            row = json.loads(line)
            if len(row.get("choices", [{}])[0].get("turns", [])) == 2:
                existing[row["question_id"]] = row
    questions = [json.loads(line) for line in args.questions.read_text().splitlines() if line]
    think = cfg.get("chat_template", {}).get("enable_thinking")
    with output.open("a") as fout:
        for q in questions:
            if q["question_id"] in existing:
                continue
            t1_prompt = render(tokenizer, [{"role": "user", "content": q["turns"][0]}], think)
            answer1 = clean_answer(complete(cfg, t1_prompt))
            messages = [
                {"role": "user", "content": q["turns"][0]},
                {"role": "assistant", "content": answer1},
                {"role": "user", "content": q["turns"][1]},
            ]
            t2_prompt = render(tokenizer, messages, think)
            answer2 = clean_answer(complete(cfg, t2_prompt))
            row = {
                "question_id": q["question_id"],
                "model_id": model_id,
                "choices": [{"index": 0, "turns": [answer1, answer2]}],
                "tstamp": time.time(),
            }
            fout.write(json.dumps(row, ensure_ascii=False) + "\n")
            fout.flush()
            print(f"{model_id}: question {q['question_id']} complete")


if __name__ == "__main__":
    main()

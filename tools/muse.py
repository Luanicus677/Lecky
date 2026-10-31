#!/usr/bin/env python3
"""Send one prompt to Meta's Muse Spark model and print the answer.

Usage:  python3 tools/muse.py "prompt text"      (or the prompt on stdin)
        python3 tools/muse.py --standard ...      (Standard tier: Meta does not train on it)

The API key is NOT read here: the Claude environment's network secret adds the
Authorization header to requests for api.meta.ai. The default model is the cheap
Contributor tier, which lets Meta train on prompts and answers, so send only
public-domain material (Lecky, old sources), never personal data or keys.
Muse spends many tokens "reasoning" before it answers, hence the large max_tokens.
"""
import json
import sys
import urllib.request

API = "https://api.meta.ai/v1/chat/completions"


def ask(prompt, model="muse-spark-1.3-contributor", max_tokens=8000, system=None):
    messages = ([{"role": "system", "content": system}] if system else []) + [
        {"role": "user", "content": prompt}
    ]
    body = json.dumps({"model": model, "messages": messages, "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(API, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.load(r)
    choice = d["choices"][0]
    if choice.get("finish_reason") == "length" and not choice["message"].get("content"):
        raise RuntimeError("ran out of tokens while reasoning; raise max_tokens")
    return choice["message"]["content"], d.get("usage", {})


if __name__ == "__main__":
    args = sys.argv[1:]
    model = "muse-spark-1.3-contributor"
    if args and args[0] == "--standard":
        model, args = "muse-spark-1.3", args[1:]
    prompt = " ".join(args) if args else sys.stdin.read()
    text, usage = ask(prompt, model=model)
    print(text)
    print("\n[usage]", json.dumps(usage), file=sys.stderr)

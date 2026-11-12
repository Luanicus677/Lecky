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


def ask(prompt, model="muse-spark-1.3-contributor", max_tokens=8000, system=None, stream=True):
    """Return (answer text, usage dict).

    stream=True (the default) asks for a streamed reply. The Claude environment's proxy drops a
    request that has had no response for about 30 seconds, and Muse often reasons for longer than
    that before it writes anything; a streamed reply opens the response at once, so it survives.
    """
    messages = ([{"role": "system", "content": system}] if system else []) + [
        {"role": "user", "content": prompt}
    ]
    payload = {"model": model, "messages": messages, "max_tokens": max_tokens}
    if stream:
        payload.update({"stream": True, "stream_options": {"include_usage": True}})
    req = urllib.request.Request(API, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        if not stream:
            d = json.load(r)
            choice = d["choices"][0]
            if choice.get("finish_reason") == "length" and not choice["message"].get("content"):
                raise RuntimeError("ran out of tokens while reasoning; raise max_tokens")
            return choice["message"]["content"], d.get("usage", {})
        text, usage, finish = "", {}, None
        for raw in r:
            line = raw.decode("utf-8", "replace").strip()
            if not line.startswith("data:") or line == "data: [DONE]":
                continue
            try:
                d = json.loads(line[5:])
            except ValueError:
                continue
            if d.get("error"):
                raise RuntimeError(str(d["error"])[:300])
            usage = d.get("usage") or usage
            for ch in d.get("choices") or []:
                text += (ch.get("delta") or {}).get("content") or ""
                finish = ch.get("finish_reason") or finish
    if not text:
        raise RuntimeError("empty answer" + ("; ran out of tokens while reasoning, raise max_tokens" if finish == "length" else ""))
    return text, usage


if __name__ == "__main__":
    args = sys.argv[1:]
    model = "muse-spark-1.3-contributor"
    if args and args[0] == "--standard":
        model, args = "muse-spark-1.3", args[1:]
    prompt = " ".join(args) if args else sys.stdin.read()
    text, usage = ask(prompt, model=model)
    print(text)
    print("\n[usage]", json.dumps(usage), file=sys.stderr)

import json
import time
import llm
from constant import KEEP_RECENT, PRESERVE_RESULT_TOOLS, TRANSCRIPT_DIR
from langchain_core.messages import SystemMessage, ToolMessage

def estimate_tokens(messages: list) -> int:
    return len(json.dumps(messages, default=str)) // 4

def micro_compact(messages: list):
    indices_ids = [idx for idx, msg in enumerate(messages) if isinstance(msg, ToolMessage)]
    if len(indices_ids) <= KEEP_RECENT:
        return messages
    for idx in indices_ids[:-KEEP_RECENT]:
        if len(messages[idx].content) <= 100:
            continue
        tool_name = getattr(messages[idx], "name", None)
        if tool_name in PRESERVE_RESULT_TOOLS:
            continue
        messages[idx].content = f"[Previous tool result compressed: {tool_name}."
    return messages

def auto_compact(messages: list) -> list:
    TRANSCRIPT_DIR.mkdir(exist_ok=True)
    path = TRANSCRIPT_DIR / f"transcript_{int(time.time())}.jsonl"
    with open(path, "w") as f:
        for msg in messages:
            f.write(json.dumps(msg, default=str) + "\n")
    conv_text = json.dumps(messages, default=str)[-80000:]
    prompt = """Summarize this conversation for continuity. Include: 
            1) What was accomplished, 2) Current state, 3) Key decisions made.
            Be concise but preserve critical details.\n\n""" + conv_text
    resp = llm.LLM().ChatOpenAI(temperature=0).bind(max_tokens=8000).invoke(prompt)
    summary = "No summary generated."
    if len(resp.content) > 0:
        summary = resp.content.strip()
    messages = [SystemMessage(content=f"[Conversation compressed. Transcript: {path}]\n\n{summary}")]
    return messages

import json
import time
from typing import Any

import llm
from constant import KEEP_RECENT, PRESERVE_RESULT_TOOLS, THRESHOLD, TRANSCRIPT_DIR
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

def estimate_tokens(messages: list) -> int:
    return len(str(messages)) // 4

def should_compact(messages: list) -> bool:
    return estimate_tokens(messages) >= THRESHOLD

def micro_compact(messages: list) -> list:
    tool_indices = [idx for idx, msg in enumerate(messages) if isinstance(msg, ToolMessage)]
    if len(tool_indices) <= KEEP_RECENT:
        return messages

    for idx in tool_indices[:-KEEP_RECENT]:
        tool_msg = messages[idx]
        if len(tool_msg.content) <= 100:
            continue
        tool_name = getattr(tool_msg, "name", None)
        tool_call_id = getattr(tool_msg, "tool_call_id", None)
        if tool_name in PRESERVE_RESULT_TOOLS:
            continue
        messages[idx] = ToolMessage(
            content=f"[Previous tool result compressed: {tool_name}; ",
            name=tool_name,
            tool_call_id=tool_call_id,
        )
    return messages


def auto_compact(messages: list) -> list:
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    transcript_path = TRANSCRIPT_DIR / f"transcript_{int(time.time())}.jsonl"
    with open(transcript_path, "w") as f:
        for msg in messages:
            f.write(json.dumps(msg, default=str) + "\n")
    print(f"[transcript saved: {transcript_path}]")

    conversation_text = json.dumps(messages, default=str)[-80000:]
    summarizer = llm.LLM().ChatOpenAI(temperature=0)
    prompt = """Summarize this conversation for continuity. Include: 
            1) What was accomplished, 2) Current state, 3) Key decisions made.
            Be concise but preserve critical details.\n\n""" + conversation_text
    summary_response = summarizer.invoke(prompt)
    summary = "No summary generated."
    if len(summary_response.content) > 0:
        summary = summary_response.content.strip()
    messages = [SystemMessage(content=f"[Conversation compressed. Transcript: {transcript_path}]\n\n{summary}")]
    return messages

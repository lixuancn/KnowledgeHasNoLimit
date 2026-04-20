#!/usr/bin/env python3
# Harness: the loop -- the model's first connection to the real world.
"""
s01_agent_loop.py - The Agent Loop

The entire secret of an AI coding agent in one pattern:

    while stop_reason == "tool_use":
        response = LLM(messages, tools)
        execute tools
        append results

    +----------+      +-------+      +---------+
    |   User   | ---> |  LLM  | ---> |  Tool   |
    |  prompt  |      |       |      | execute |
    +----------+      +---+---+      +----+----+
                          ^               |
                          |   tool_result |
                          +---------------+
                          (loop continues)

This is the core loop: feed tool results back to the model
until the model decides to stop. Production agents layer
policy, hooks, and lifecycle controls on top.
"""

import os
import subprocess
import llm

try:
    import readline
    # #143 UTF-8 backspace fix for macOS libedit
    readline.parse_and_bind('set bind-tty-special-chars off')
    readline.parse_and_bind('set input-meta on')
    readline.parse_and_bind('set output-meta on')
    readline.parse_and_bind('set convert-meta off')
except ImportError:
    pass

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

load_dotenv(override=True)

SYSTEM = f"You are a coding agent at {os.getcwd()}. Use bash to solve tasks. Act, don't explain."

TOOLS = [{
    "type": "function",
    "function": {
        "name": "bash",
        "description": "Run a shell command.",
        "parameters": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
}]

client = llm.LLM().ChatOpenAI()
client_with_tools = client.bind_tools(TOOLS).bind(max_tokens=8000)

def run_bash(command: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        r = subprocess.run(command, shell=True, cwd=os.getcwd(),
                           capture_output=True, text=True, timeout=120)
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"
    except (FileNotFoundError, OSError) as e:
        return f"Error: {e}"


# -- The core pattern: a while loop that calls tools until the model stops --
def agent_loop(messages: list):
    round = 0
    while True:
        print(f"第{round}轮，messages:", messages)
        round += 1
        response = client_with_tools.invoke(messages)
        print(f"第{round}轮，response:", response)
        messages.append(response)
        if not response.tool_calls:
            return
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            if tool_name == "bash":
                command = tool_args["command"]
                print(f"\033[33m$ {command}\033[0m")
                output = run_bash(command)
                print(output[:200])
                messages.append(ToolMessage(content=output, tool_call_id=tool_call["id"]))

if __name__ == "__main__":
    history = [SystemMessage(content=SYSTEM)]
    while True:
        try:
            query = input("\033[36ms01 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        history.append(HumanMessage(content=query))
        agent_loop(history)
        response_content = history[-1].content
        print(f"最终结果：{response_content}")

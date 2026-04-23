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

import llm
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from constant import TODO_REMINDER, WORKDIR
from tool import PARENT_TOOLS, TOOL_HANDLERS
from skill import SKILL_LOADER

try:
    import readline
    # #143 UTF-8 backspace fix for macOS libedit
    readline.parse_and_bind('set bind-tty-special-chars off')
    readline.parse_and_bind('set input-meta on')
    readline.parse_and_bind('set output-meta on')
    readline.parse_and_bind('set convert-meta off')
except ImportError:
    pass

load_dotenv(override=True)
SYSTEM = f"""You are a coding agent at {WORKDIR}. Use bash to solve tasks. Act, don't explain.
Skills available:
{SKILL_LOADER.get_descriptions()}"""




client = llm.LLM().ChatOpenAI()
client_with_tools = client.bind_tools(PARENT_TOOLS).bind(max_tokens=8000)


# -- The core pattern: a while loop that calls tools until the model stops --
def agent_loop(messages: list):
    rounds = 0
    rounds_without_todo = 0
    while True:
        rounds += 1
        response = client_with_tools.invoke(messages)
        print(f"主体第{rounds}轮。大模型响应：content={response.content}")
        messages.append(response)
        if not response.tool_calls:
            return
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            print(f"主体第{rounds}轮。工具调用：{tool_name}({tool_args})")
            handler = TOOL_HANDLERS.get(tool_name)
            if handler is None:
                output = f"Error: Unknown tool '{tool_name}'"
            else:
                print(f"\033[33m$ 主体第{rounds}轮。执行工具：{tool_name}({tool_args})\033[0m")
                output = handler(**tool_args)
                print(f"主体第{rounds}轮。工具结果：{output[:200]}")
            if tool_name == 'todo':
                rounds_without_todo = 0
            else:
                rounds_without_todo += 1
            messages.append(ToolMessage(content=output, tool_call_id=tool_call["id"]))
        if rounds_without_todo >= 3:
            messages.append(HumanMessage(content=TODO_REMINDER))
            print(f"主体第{rounds}轮。已注入 todo reminder")
            rounds_without_todo = 0

if __name__ == "__main__":
    while True:
        try:
            query = input("\033[36ms01 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        history = [SystemMessage(content=SYSTEM), HumanMessage(content=query)]
        print(f"进入核心循环的消息：{history}")
        agent_loop(history)
        response_content = history[-1].content
        print(f"最终结果：{response_content}")

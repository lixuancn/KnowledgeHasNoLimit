
#!/usr/bin/env python3
# Harness: the loop -- the model's first connection to the real world.

from constant import WORKDIR, TOKEN_THRESHOLD
import json
from tool.definition import BackgroundManage, TodoManage, SkillLoade, MessageBus, TaskManage, TeammateManage
from tool.definition import get_lead_tools, get_lead_tool_handlers, get_subagent_tools, get_subagent_tool_handlers, get_teammate_tools, get_teammate_tool_handlers
from tool.tool_compact import auto_compact, micro_compact, estimate_tokens
import llm
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

# === SECTION: system_prompt ===
SYSTEM_PROMPT = f"""You name is lead. You are a coding agent at {WORKDIR}. Use tools to solve tasks.
Prefer task_create/task_update/task_list for multi-step work. Use todo_write for short checklists.
Use task for subagent delegation. Use load_skill for specialized knowledge.
Skills: {SkillLoade.descriptions()}"""

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

client = llm.LLM().ChatOpenAI()
client_with_tools = client.bind_tools(get_lead_tools()).bind(max_tokens=8000)


# -- The core pattern: a while loop that calls tools until the model stops --
def agent_loop(messages: list):
    rounds = 0
    rounds_without_todo = 0
    while True:
        rounds += 1
        messages[:] = micro_compact(messages)
        print(f"主体第{rounds}轮。第一层压缩后消息：{messages}")
        if estimate_tokens(messages) > TOKEN_THRESHOLD:
            print("[auto-compact triggered]")
            messages[:] = auto_compact(messages)
            print(f"\033[33m$ 主体第{rounds}轮。第二层压缩后消息：{messages}\033[0m")
        # 后台任务
        notifs = BackgroundManage.drain()        
        if notifs:
            txt = "\n".join(f"[bg:{n['task_id']}] {n['status']}: {n['result']}" for n in notifs)
            txt = f"<background-results>\n{txt}\n</background-results>"
            messages.append(ToolMessage(content=txt, name="background_check", tool_call_id="background_check"))
        # 收件箱
        inbox = MessageBus.read_inbox("lead")
        if inbox:
            messages.append(HumanMessage(content=f"<inbox>{json.dumps(inbox, indent=2)}</inbox>"))
        # 压缩消息
        response = client_with_tools.invoke(messages)
        print(f"\033[33m$ 主体第{rounds}轮。大模型响应：content={response.content}\033[0m")
        messages.append(response)
        if not response.tool_calls:
            return
        results = []
        used_todo = False
        manual_compress = False
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            print(f"\033[33m$ 主体第{rounds}轮。工具调用：{tool_name}({tool_args})\033[0m")
            handler = get_lead_tool_handlers().get(tool_name)
            if handler is None:
                output = f"Error: Unknown tool '{tool_name}'"
            else:
                print(f"\033[33m$ 主体第{rounds}轮。执行工具：{tool_name}({tool_args})\033[0m")
                output = handler(**tool_args)
                print(f"\033[33m$ 主体第{rounds}轮。工具结果：{output[:200]}\033[0m")
            if tool_name == "compress":
                manual_compress = True
            elif tool_name == "todo_write":
                used_todo = True
            messages.append(ToolMessage(content=output, name=tool_name, tool_call_id=tool_call["id"]))        
        rounds_without_todo = 0 if used_todo else rounds_without_todo + 1
        if TodoManage.has_open_items() and rounds_without_todo >= 3:
            messages.append(HumanMessage(content="<reminder>Update your todos.</reminder>"))
            print(f"\033[33m$ 主体第{rounds}轮。已注入 todo reminder\033[0m")
            rounds_without_todo = 0
        if manual_compress:
            print("[manual compact]")
            messages[:] = auto_compact(messages)
            return

if __name__ == "__main__":
    history = []
    known_commands = {"/team", "/inbox", "/new", "/tasks"}
    while True:
        try:
            query = input("\033[36ms01 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        if query.strip() == "/compact":
            if history:
                print("[manual compact via /compact]")
                history[:] = auto_compact(history)
                print(f"压缩后消息：{history}")
            continue
        if query.strip() == "/tasks":
            print(TaskManage.list_all())
            continue
        if query.strip() == "/team":
            print(TeammateManage.list_all())
            continue
        elif query.strip() == "/inbox":
            print(json.dumps(MessageBus.read_inbox("lead"), indent=2))
            continue
        elif query.strip() == "/new":
            history = []
            continue
        elif query.strip().startswith("/") and query.strip() not in known_commands:
            print(f"Error: Unknown command '{query.strip()}'")
            continue
        if history is None or len(history) == 0:
            history = [SystemMessage(content=SYSTEM_PROMPT)]
        history.append(HumanMessage(content=query))
        print(f"进入核心循环的消息：{history}")
        agent_loop(history)
        response_content = history[-1].content
        print(f"最终结果：{response_content}")

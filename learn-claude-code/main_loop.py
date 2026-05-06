
#!/usr/bin/env python3
# Harness: the loop -- the model's first connection to the real world.
from constant import TASKS_DIR
from agent_teams import TeammateManage
import json
from tool_background import BackgroundManage
from compact import auto_compact, micro_compact, should_compact
import llm
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from constant import ENABLE_COMPACT, TODO_REMINDER, WORKDIR
from tool import LEAD_TOOLS, LEAD_TOOL_HANDLERS
from skill import SKILL_LOADER
from agent_teams import MessageBus



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
SYSTEM = f"""your name is lead，You are a coding agent at {WORKDIR}. Use task tools to plan and track work, Use background_run for long-running commands.  Spawn teammates and communicate via inboxes.
Skills available:
{SKILL_LOADER.get_descriptions()}"""

client = llm.LLM().ChatOpenAI()
client_with_tools = client.bind_tools(LEAD_TOOLS).bind(max_tokens=8000)


# -- The core pattern: a while loop that calls tools until the model stops --
def agent_loop(messages: list):
    rounds = 0
    rounds_without_todo = 0
    while True:
        rounds += 1
        # 收件箱
        inbox = MessageBus.read_inbox("lead")
        if inbox:
            messages.append(HumanMessage(content=f"<inbox>{json.dumps(inbox, indent=2)}</inbox>"))
        notifs = BackgroundManage.drain_notifications()
        # 后台任务
        if notifs:
            notif_text = "\n".join(f"[bg:{n['task_id']}] {n['status']}: {n['result']}" for n in notifs)
            print("notif_text:", notif_text)
            messages.append(ToolMessage(content=notif_text, name="background_check", tool_call_id="background_check"))
        # 压缩消息
        if ENABLE_COMPACT:
            messages[:] = micro_compact(messages)
            print(f"主体第{rounds}轮。第一层压缩后消息：{messages}")
            if should_compact(messages):
                print("[auto_compact triggered]")
                messages[:] = auto_compact(messages)
                print(f"\033[33m$ 主体第{rounds}轮。第二层压缩后消息：{messages}\033[0m")
        response = client_with_tools.invoke(messages)
        print(f"\033[33m$ 主体第{rounds}轮。大模型响应：content={response.content}\033[0m")
        messages.append(response)
        if not response.tool_calls:
            return
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            print(f"\033[33m$ 主体第{rounds}轮。工具调用：{tool_name}({tool_args})\033[0m")
            handler = LEAD_TOOL_HANDLERS.get(tool_name)
            if handler is None:
                output = f"Error: Unknown tool '{tool_name}'"
            else:
                print(f"\033[33m$ 主体第{rounds}轮。执行工具：{tool_name}({tool_args})\033[0m")
                output = handler(**tool_args)
                print(f"\033[33m$ 主体第{rounds}轮。工具结果：{output[:200]}\033[0m")
            if tool_name == 'todo':
                rounds_without_todo = 0
            else:
                rounds_without_todo += 1
            messages.append(ToolMessage(content=output, name=tool_name, tool_call_id=tool_call["id"]))
        if rounds_without_todo >= 3:
            print(f"\033[33m$ 主体第{rounds}轮。已注入 todo reminder\033[0m")
            rounds_without_todo = 0

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
            history = [SystemMessage(content=SYSTEM)]
        if query.strip() == "/tasks":
            TASKS_DIR.mkdir(exist_ok=True)
            for f in sorted(TASKS_DIR.glob("task_*.json")):
                t = json.loads(f.read_text())
                marker = {"pending": "[ ]", "in_progress": "[>]", "completed": "[x]"}.get(t["status"], "[?]")
                owner = f" @{t['owner']}" if t.get("owner") else ""
                print(f"  {marker} #{t['id']}: {t['subject']}{owner}")
            continue
        history.append(HumanMessage(content=query))
        print(f"进入核心循环的消息：{history}")
        agent_loop(history)
        response_content = history[-1].content
        print(f"最终结果：{response_content}")

# -- MessageBuser: JSONL inbox per teammate --
from tool.tool_taskmanager import TaskManager
from tool.tool_messagebuser import MessageBuser
from constant import POLL_INTERVAL
from constant import IDLE_TIMEOUT
import uuid
import llm
import threading
from pathlib import Path
import time
import json
from constant import WORKDIR, TASKS_DIR
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage

shutdown_requests = {}
plan_requests = {}

class TeammateManager:
    def __init__(self, team_dir: Path, bus: MessageBuser, task_manage: TaskManager, tools: list[dict], tool_handlers: dict):
        self.dir = team_dir
        self.dir.mkdir(exist_ok=True)
        self.config_path = self.dir / "config.json"
        self.config = self._load()
        self._reset_all_member_statuses()
        self.message_bus = bus
        self.task_manage = task_manage
        self.threads = {}
        self.tool_handlers = tool_handlers
        self.client_with_tools = llm.LLM().ChatOpenAI().bind_tools(tools).bind(max_tokens=8000)

    def _normalize_name(self, name: str) -> str:
        return name.strip().casefold()

    def _load(self) -> dict:
        if self.config_path.exists():
            return json.loads(self.config_path.read_text())
        return {"team_name": "default", "members": []}

    def _save(self):
        self.config_path.write_text(json.dumps(self.config, indent=2))

    def _reset_all_member_statuses(self):
        changed = False
        for member in self.config.get("members", []):
            if member.get("status") != "shutdown":
                member["status"] = "shutdown"
                changed = True
        if changed:
            self._save()

    def _find(self, name: str) -> dict:
        name = self._normalize_name(name)
        for m in self.config["members"]:
            if self._normalize_name(m["name"]) == name: return m
        return None
    
    def _set_status(self, name: str, status: str):
        name = self._normalize_name(name)
        member = self._find(name)
        if member:
            member["status"] = status
            self._save()

    def spawn(self, name: str, role: str, prompt: str) -> str:
        name = self._normalize_name(name)
        member = self._find(name)
        if member:
            if member["status"] not in ("idle", "shutdown"):
                return f"Error: '{name}' is currently {member['status']}"
            member["status"] = "working"
            member["role"] = role
        else:
            member = {"name": name, "role": role, "status": "working"}
            self.config["members"].append(member)
        self._save()

        existing_thread = self.threads.get(name)
        if existing_thread is not None and existing_thread.is_alive():
            return f"'{name}' is already running"
        if existing_thread is not None:
            del self.threads[name]

        thread = threading.Thread(target=self._loop, args=(name, role, prompt), daemon=True)
        self.threads[name] = thread
        thread.start()
        print(f"\033[34m启动子agent：'{name}' (role: {role})")
        return f"Spawned '{name}' (role: {role})"

    def _loop(self, name: str, role: str, prompt: str):
        name = self._normalize_name(name)
        team_name = self.config["team_name"]
        sys_prompt = (f"You are '{name}', role: {role}, team: {team_name}, at {WORKDIR}. "
                      f"Use idle when done with current work. You may auto-claim tasks.")
        messages = [SystemMessage(content=sys_prompt), HumanMessage(content=prompt)]
        while True:
            # -- WORK PHASE --
            rounds = 0
            for _ in range(50):
                rounds += 1
                inbox = self.message_bus.read_inbox(name)
                for msg in inbox:
                    print(f"\033[34m$ 子agent {name} 第{rounds}轮。读取收件箱内容：{msg}\033[0m")
                    if msg.get("type") == "shutdown_request":
                        self._set_status(name, "shutdown")
                        return
                    messages.append(HumanMessage(content=json.dumps(msg)))
                try:
                    response = self.client_with_tools.invoke(messages)   
                except Exception:
                    self._set_status(name, "idle")
                    return
                print(f"\033[34m$ 子agent {name} 第{rounds}轮。大模型响应：content={response.content}\033[0m")
                messages.append(response)
                if not response.tool_calls:
                    break
                idle_requested = False
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    print(f"\033[34m$ 子agent {name} 第{rounds}轮。工具调用：{tool_name}({tool_args})\033[0m")
                    if tool_name == "idle":
                        idle_requested = True
                        output = "Entering idle phase. Will poll for new tasks."
                    elif tool_name == "claim_task":
                            output = self.task_manage.claim(tool_args["task_id"], name)
                    elif tool_name == "send_message":
                        output = self.message_bus.send(name, tool_args["to"], tool_args["content"])
                    else:
                        handler = self.tool_handlers.get(tool_name)
                        if handler is None:
                            output = f"Error: Unknown tool '{tool_name}'"
                        else:
                            print(f"\033[34m$ 子agent {name} 第{rounds}轮。执行工具：{tool_name}({tool_args})\033[0m")
                            output = handler(**tool_args)
                    print(f"\033[34m$ 子agent {name} 第{rounds}轮。工具结果：{output[:200]}\033[0m")
                    messages.append(ToolMessage(content=output, name=tool_name, tool_call_id=tool_call["id"]))
                if idle_requested:
                    break

            # -- IDLE PHASE: poll for inbox messages and unclaimed tasks --
            self._set_status(name, "idle")
            resume = False
            rounds = 0
            for _ in range(IDLE_TIMEOUT // max(POLL_INTERVAL, 1)):
                rounds += 1
                time.sleep(POLL_INTERVAL)
                inbox = self.message_bus.read_inbox(name)
                if inbox:
                    for msg in inbox:
                        print(f"\033[34m$ 子agent {name} 空闲阶段 第{rounds}轮。读取收件箱内容：{msg}\033[0m")
                        if msg.get("type") == "shutdown_request":
                            self._set_status(name, "shutdown")
                            return
                        messages.append(HumanMessage(content=json.dumps(msg)))
                    resume = True
                    break
                unclaimed = []
                for f in sorted(TASKS_DIR.glob("task_*.json")):
                    t = json.loads(f.read_text())
                    if t.get("status") == "pending" and not t.get("owner") and not t.get("blockedBy"):
                        unclaimed.append(t)
                if unclaimed:
                    task = unclaimed[0]
                    result = self.task_manage.claim(task["id"], name)
                    if result.startswith("Error:"):
                        continue
                    # Identity re-injection for compressed contexts
                    task_prompt = (
                        f"<auto-claimed>Task #{task['id']}: {task['subject']}\n"
                        f"{task.get('description', '')}</auto-claimed>"
                    )
                    print(f"\033[34m$ 子agent {name} 空闲阶段 第{rounds}轮。认领任务内容：{task_prompt}\033[0m")
                    if len(messages) <= 3:
                        messages.insert(0, HumanMessage(content=f"<identity>You are '{name}', role: {role}, team: {team_name}. Continue your work.</identity>"))
                        messages.insert(1, AIMessage(content=f"I am {name}. Continuing."))
                    messages.append(HumanMessage(content=task_prompt))
                    messages.append(AIMessage(content=f"Claimed task #{task['id']}. Working on it."))
                    resume = True
                    break
            if not resume:
                self._set_status(name, "shutdown")
                return
            self._set_status(name, "working")

    def list_all(self) -> str:
        if not self.config["members"]:
            return "No teammates."
        lines = [f"Team: {self.config['team_name']}"]
        for m in self.config["members"]:
            lines.append(f"  {m['name']} ({m['role']}): {m['status']}")
        return "\n".join(lines)

    def member_names(self) -> list:
        return [m["name"] for m in self.config["members"]]
    
    # === SECTION: shutdown_protocol (s10) ===
    def handle_shutdown_request(self, teammate: str) -> str:
        teammate = self._normalize_name(teammate)
        req_id = str(uuid.uuid4())[:8]
        shutdown_requests[req_id] = {"target": teammate, "status": "pending"}
        self.message_bus.send("lead", teammate, "Please shut down.", "shutdown_request", {"request_id": req_id})
        return f"Shutdown request {req_id} sent to '{teammate}'"

    # === SECTION: plan_approval (s10) ===
    def handle_plan_review(self, request_id: str, approve: bool, feedback: str = "") -> str:
        teammate = self._normalize_name(teammate)
        req = plan_requests.get(request_id)
        if not req: 
            return f"Error: Unknown plan request_id '{request_id}'"
        req["status"] = "approved" if approve else "rejected"
        self.message_bus.send("lead", req["from"], feedback, "plan_approval_response",
                {"request_id": request_id, "approve": approve, "feedback": feedback})
        return f"Plan {req['status']} for '{req['from']}'"

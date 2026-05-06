# -- MessageBuser: JSONL inbox per teammate --
from constant import POLL_INTERVAL
from constant import IDLE_TIMEOUT
import uuid
from constant import TEAM_DIR
from tool import TEAMMATE_TOOLS, TEAMMATE_TOOL_HANDLERS
import llm
import threading
from pathlib import Path
import time
import json
from constant import VALID_MSG_TYPES, INBOX_DIR, WORKDIR, TASKS_DIR
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage


def _normalize_name(name: str) -> str:
    return name.strip().casefold()


class MessageBuser:
    def __init__(self, inbox_dir: Path):
        self.dir = inbox_dir
        self.dir.mkdir(parents=True, exist_ok=True)

    def _inbox_path(self, name: str) -> Path:
        return self.dir / f"{_normalize_name(name)}.jsonl"

    def send(self, sender: str, to: str, content: str,
             msg_type: str = "message", extra: dict = None) -> str:
        if msg_type not in VALID_MSG_TYPES:
            return f"Error: Invalid type '{msg_type}'. Valid: {VALID_MSG_TYPES}"
        msg = {
            "type": msg_type,
            "from": sender,
            "content": content,
            "timestamp": time.time(),
        }
        if extra:
            msg.update(extra)
        inbox_path = self._inbox_path(to)
        with open(inbox_path, "a") as f:
            f.write(json.dumps(msg) + "\n")
        return f"Sent {msg_type} to {to}"

    def read_inbox(self, name: str) -> list:
        inbox_path = self._inbox_path(name)
        if not inbox_path.exists():
            return []
        messages = []
        for line in inbox_path.read_text().strip().splitlines():
            if line:
                messages.append(json.loads(line))
        inbox_path.write_text("")
        return messages

    def broadcast(self, sender: str, content: str, teammates: list) -> str:
        count = 0
        for name in teammates:
            if _normalize_name(name) != _normalize_name(sender):
                self.send(sender, name, content, "broadcast")
                count += 1
        return f"Broadcast to {count} teammates"

MessageBus = MessageBuser(INBOX_DIR)

shutdown_requests = {}
plan_requests = {}
_tracker_lock = threading.Lock()
_claim_lock = threading.Lock()



# -- TeammateManager: persistent named agents with config.json --
class TeammateManager:
    def __init__(self, team_dir: Path):
        self.dir = team_dir
        self.dir.mkdir(exist_ok=True)
        self.config_path = self.dir / "config.json"
        self.config = self._load_config()
        self.threads = {}
        self.client_with_tools = llm.LLM().ChatOpenAI().bind_tools(TEAMMATE_TOOLS).bind(max_tokens=8000)

    def _load_config(self) -> dict:
        if self.config_path.exists():
            return json.loads(self.config_path.read_text())
        return {"team_name": "default", "members": []}

    def _save_config(self):
        self.config_path.write_text(json.dumps(self.config, indent=2))

    def _find_member(self, name: str) -> dict:
        normalized_name = _normalize_name(name)
        for m in self.config["members"]:
            if _normalize_name(m["name"]) == normalized_name:
                return m
        return None
    
    def _set_status(self, name: str, status: str):
        member = self._find_member(name)
        if member:
            member["status"] = status
            self._save_config()

    def spawn(self, name: str, role: str, prompt: str) -> str:
        # Step 1: ensure the member exists in config and persist its working state.
        member = self._find_member(name)
        if member:
            member["status"] = "working"
            member["role"] = role
            canonical_name = member["name"]
        else:
            member = {"name": name, "role": role, "status": "working"}
            self.config["members"].append(member)
            canonical_name = name
        self._save_config()

        # Step 2: reuse a live thread if present; otherwise start a fresh one.
        thread_key = _normalize_name(canonical_name)
        existing_thread = self.threads.get(thread_key)
        if existing_thread is not None and existing_thread.is_alive():
            return f"'{canonical_name}' is already running"
        if existing_thread is not None:
            del self.threads[thread_key]

        thread = threading.Thread(
            target=self._teammate_loop,
            args=(canonical_name, role, prompt),
            daemon=True,
        )
        self.threads[thread_key] = thread
        thread.start()
        print(f"\033[34m启动子agent：'{canonical_name}' (role: {role})")
        return f"Spawned '{canonical_name}' (role: {role})"

    def _teammate_loop(self, name: str, role: str, prompt: str):
        name = _normalize_name(name)
        team_name = self.config["team_name"]
        sys_prompt = (
             f"You are '{name}', role: {role}, team: {team_name}, at {WORKDIR}. "
            f"Use idle tool when you have no more work. You will auto-claim new tasks."
        )
        messages = [SystemMessage(content=sys_prompt), HumanMessage(content=prompt)]
        while True:
            rounds = 0
            for _ in range(50):
                rounds += 1
                inbox = MessageBus.read_inbox(name)
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
                    else:
                        handler = TEAMMATE_TOOL_HANDLERS.get(tool_name)
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
            polls = IDLE_TIMEOUT // max(POLL_INTERVAL, 1)
            rounds = 0
            for _ in range(polls):
                rounds += 1
                time.sleep(POLL_INTERVAL)
                inbox = MessageBus.read_inbox(name)
                if inbox:
                    for msg in inbox:
                        print(f"\033[34m$ 子agent {name} 空闲阶段 第{rounds}轮。读取收件箱内容：{msg}\033[0m")
                        if msg.get("type") == "shutdown_request":
                            self._set_status(name, "shutdown")
                            return
                        messages.append(HumanMessage(content=json.dumps(msg)))
                    resume = True
                    break
                unclaimed = self.scan_unclaimed_tasks()
                if unclaimed:
                    task = unclaimed[0]
                    result = self.claim_task(task["id"], name)
                    if result.startswith("Error:"):
                        continue
                    task_prompt = (
                        f"<auto-claimed>Task #{task['id']}: {task['subject']}\n"
                        f"{task.get('description', '')}</auto-claimed>"
                    )
                    print(f"\033[34m$ 子agent {name} 空闲阶段 第{rounds}轮。认领任务内容：{task_prompt}\033[0m")
                    if len(messages) <= 3:
                        messages.insert(0, self.make_identity_block(name, role, team_name))
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
    
    def shutdown_response(self, sender: str, request_id: str, approve: bool, reason: str = None) -> str:
        req_id = request_id
        with _tracker_lock:
            if req_id in shutdown_requests:
                shutdown_requests[req_id]["status"] = "approved" if approve else "rejected"
            MessageBus.send(sender, "lead", reason, "shutdown_response", {"request_id": req_id, "approve": approve})
            return f"Shutdown {'approved' if approve else 'rejected'}"

    def plan_approval(self, sender: str, plan_text: str) -> str:
        req_id = str(uuid.uuid4())[:8]
        with _tracker_lock:
            plan_requests[req_id] = {"from": sender, "plan": plan_text, "status": "pending"}
        MessageBus.send(sender, "lead", plan_text, "plan_approval_response", {"request_id": req_id, "plan": plan_text})
        return f"Plan submitted (request_id={req_id}). Waiting for lead approval."

    def scan_unclaimed_tasks(self) -> list:
        TASKS_DIR.mkdir(exist_ok=True)
        unclaimed = []
        for f in sorted(TASKS_DIR.glob("task_*.json")):
            task = json.loads(f.read_text())
            if (task.get("status") == "pending"
                    and not task.get("owner")
                    and not task.get("blockedBy")):
                unclaimed.append(task)
        return unclaimed


    def claim_task(self, task_id: int, owner: str) -> str:
        with _claim_lock:
            path = TASKS_DIR / f"task_{task_id}.json"
            if not path.exists():
                return f"Error: Task {task_id} not found"
            task = json.loads(path.read_text())
            if task.get("owner"):
                existing_owner = task.get("owner") or "someone else"
                return f"Error: Task {task_id} has already been claimed by {existing_owner}"
            if task.get("status") != "pending":
                status = task.get("status")
                return f"Error: Task {task_id} cannot be claimed because its status is '{status}'"
            if task.get("blockedBy"):
                return f"Error: Task {task_id} is blocked by other task(s) and cannot be claimed yet"
            task["owner"] = owner
            task["status"] = "in_progress"
            path.write_text(json.dumps(task, indent=2))
        return f"Claimed task #{task_id} for {owner}"

    # -- Identity re-injection after compression --
    def make_identity_block(self, name: str, role: str, team_name: str) -> HumanMessage:
        return HumanMessage(
            content=f"<identity>You are '{name}', role: {role}, team: {team_name}. Continue your work.</identity>",
        )

TeammateManage = TeammateManager(TEAM_DIR)

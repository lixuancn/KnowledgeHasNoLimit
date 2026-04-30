# -- MessageBuser: JSONL inbox per teammate --
import uuid
from constant import TEAM_DIR
from tool import TEAMMATE_TOOLS, TEAMMATE_TOOL_HANDLERS
import llm
import threading
from pathlib import Path
import time
import json
from constant import VALID_MSG_TYPES, INBOX_DIR, WORKDIR
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage



class MessageBuser:
    def __init__(self, inbox_dir: Path):
        self.dir = inbox_dir
        self.dir.mkdir(parents=True, exist_ok=True)

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
        inbox_path = self.dir / f"{to}.jsonl"
        with open(inbox_path, "a") as f:
            f.write(json.dumps(msg) + "\n")
        return f"Sent {msg_type} to {to}"

    def read_inbox(self, name: str) -> list:
        inbox_path = self.dir / f"{name}.jsonl"
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
            if name != sender:
                self.send(sender, name, content, "broadcast")
                count += 1
        return f"Broadcast to {count} teammates"

MessageBus = MessageBuser(INBOX_DIR)

shutdown_requests = {}
plan_requests = {}
_tracker_lock = threading.Lock()

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
        for m in self.config["members"]:
            if m["name"] == name:
                return m
        return None

    def spawn(self, name: str, role: str, prompt: str) -> str:
        # Step 1: ensure the member exists in config and persist its working state.
        member = self._find_member(name)
        if member:
            member["status"] = "working"
            member["role"] = role
        else:
            member = {"name": name, "role": role, "status": "working"}
            self.config["members"].append(member)
        self._save_config()

        # Step 2: reuse a live thread if present; otherwise start a fresh one.
        existing_thread = self.threads.get(name)
        if existing_thread is not None and existing_thread.is_alive():
            return f"'{name}' is already running"
        if existing_thread is not None:
            del self.threads[name]

        thread = threading.Thread(
            target=self._teammate_loop,
            args=(name, role, prompt),
            daemon=True,
        )
        self.threads[name] = thread
        thread.start()
        print(f"\033[34m启动子agent：'{name}' (role: {role})")
        return f"Spawned '{name}' (role: {role})"

    def _teammate_loop(self, name: str, role: str, prompt: str):
        sys_prompt = (
            f"You are '{name}', role: {role}, at {WORKDIR}. "
            f"Use send_message to communicate. Complete your task."
            f"Submit plans via plan_approval before major work."
            f"Respond to shutdown_request with shutdown_response."
        )
        messages = [SystemMessage(content=sys_prompt), HumanMessage(content=prompt)]
        rounds = 0
        should_exit = False
        for _ in range(50):
            rounds += 1
            inbox = MessageBus.read_inbox(name)
            for msg in inbox:
                print(f"\033[34m$ 子agent {name} 第{rounds}轮。读取收件箱内容：{msg}\033[0m")
                messages.append(HumanMessage(content=json.dumps(msg)))
            if should_exit:
                break
            try:
                response = self.client_with_tools.invoke(messages)   
            except Exception:
                break
            print(f"\033[34m$ 子agent {name} 第{rounds}轮。大模型响应：content={response.content}\033[0m")
            messages.append(response)
            if not response.tool_calls:
                return
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                print(f"\033[34m$ 子agent {name} 第{rounds}轮。工具调用：{tool_name}({tool_args})\033[0m")
                handler = TEAMMATE_TOOL_HANDLERS.get(tool_name)
                if handler is None:
                    output = f"Error: Unknown tool '{tool_name}'"
                else:
                    print(f"\033[33m$ 子agent {name} 第{rounds}轮。执行工具：{tool_name}({tool_args})\033[0m")
                    output = handler(**tool_args)
                print(f"\033[34m$ 子agent {name} 第{rounds}轮。工具结果：{output[:200]}\033[0m")
                messages.append(ToolMessage(content=output, name=tool_name, tool_call_id=tool_call["id"]))
                if tool_name == "shutdown_response" and tool_args.get("approve"):
                    should_exit = True
        member = self._find_member(name)
        if member:
            member["status"] = "shutdown" if should_exit else "idle"
            self._save_config()

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

TeammateManage = TeammateManager(TEAM_DIR)

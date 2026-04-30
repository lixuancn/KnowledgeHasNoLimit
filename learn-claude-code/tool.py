import uuid
from constant import VALID_MSG_TYPES
import json
from tool_background import BackgroundManage
from tool_taskmanager import TASKS
from pathlib import Path
import subprocess
from tool_todo import todo
from constant import WORKDIR
from skill import SKILL_LOADER


def _message_bus():
    from agent_teams import MessageBus
    return MessageBus


def _teammate_manage():
    from agent_teams import TeammateManage
    return TeammateManage

def _tracker_lock():
    from agent_teams import _tracker_lock
    return _tracker_lock

def _shutdown_requests():
    from agent_teams import shutdown_requests
    return shutdown_requests

def _plan_requests():
    from agent_teams import plan_requests
    return plan_requests

def safe_path(p: str) -> Path:
    path = (WORKDIR / p).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path


def run_bash(command: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        r = subprocess.run(
            command,
            shell=True,
            cwd=WORKDIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"
    except (FileNotFoundError, OSError) as e:
        return f"Error: {e}"


def run_read(path: str, limit: int = None) -> str:
    try:
        text = safe_path(path).read_text()
        lines = text.splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
        return "\n".join(lines)[:50000]
    except Exception as e:
        return f"Error: {e}"


def run_write(path: str, content: str) -> str:
    try:
        fp = safe_path(path)
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content)
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {e}"


def run_edit(path: str, old_text: str, new_text: str) -> str:
    try:
        fp = safe_path(path)
        content = fp.read_text()
        if old_text not in content:
            return f"Error: Text not found in {path}"
        fp.write_text(content.replace(old_text, new_text, 1))
        return f"Edited {path}"
    except Exception as e:
        return f"Error: {e}"
    
# -- Lead-specific protocol handlers --
def handle_shutdown_request(teammate: str) -> str:
    req_id = str(uuid.uuid4())[:8]
    with _tracker_lock():
        _shutdown_requests()[req_id] = {"target": teammate, "status": "pending"}
    _message_bus().send("lead", teammate, "Please shut down gracefully.", "shutdown_request", {"request_id": req_id},)
    return f"Shutdown request {req_id} sent to '{teammate}' (status: pending)"

def check_shutdown_status(request_id: str) -> str:
    with _tracker_lock():
        return json.dumps(_shutdown_requests().get(request_id, {"error": "not found"}))

def handle_plan_review(request_id: str, approve: bool, feedback: str = "") -> str:
    with _tracker_lock():
        req = _plan_requests().get(request_id)
    if not req:
        return f"Error: Unknown plan request_id '{request_id}'"
    with _tracker_lock():
        req["status"] = "approved" if approve else "rejected"
    _message_bus().send("lead", req["from"], feedback, "plan_approval_response", {"request_id": request_id, "approve": approve, "feedback": feedback})
    return f"Plan {req['status']} for '{req['from']}'"

ALL_TOOL_HANDLERS = {
    "bash": lambda **kw: run_bash(kw["command"]),
    "read_file": lambda **kw: run_read(kw["path"], kw.get("limit")),
    "write_file": lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file": lambda **kw: run_edit(kw["path"], kw["old_text"], kw["new_text"]),
    "todo": lambda **kw: todo.update(kw["items"]),
    "load_skill": lambda **kw: SKILL_LOADER.get_content(kw["name"]),
    "task_create": lambda **kw: TASKS.create(kw["subject"], kw.get("description", "")),
    "task_update": lambda **kw: TASKS.update(kw["task_id"], kw.get("status"), kw.get("addBlockedBy"), kw.get("removeBlockedBy")),
    "task_list":   lambda **_: TASKS.list_all(),
    "task_get":    lambda **kw: TASKS.get(kw["task_id"]),
    "background_run":   lambda **kw: BackgroundManage.run(kw["command"]),
    "background_check": lambda **kw: BackgroundManage.check(kw.get("task_id")),
    "send_message": lambda **kw: _message_bus().send(kw["sender"], kw["to"], kw["content"], kw.get("msg_type", "message")),
    "read_inbox": lambda **kw: json.dumps(_message_bus().read_inbox(kw["name"]), indent=2),
    "broadcast": lambda **kw: _message_bus().broadcast("lead", kw["content"], _teammate_manage().member_names()),
    "spawn_teammate": lambda **kw: _teammate_manage().spawn(kw["name"], kw["role"], kw["prompt"]),
    "list_teammates": lambda **_: _teammate_manage().list_all(),
    "shutdown_response": lambda **kw: _teammate_manage().shutdown_response(kw["sender"], kw["request_id"], kw["approve"], kw.get("reason")),
    "plan_approval": lambda **kw: _teammate_manage().plan_approval(kw["sender"], kw["plan_text"]),
    "shutdown_request":  lambda **kw: handle_shutdown_request(kw["teammate"]),
    "check_shutdown_status": lambda **kw: check_shutdown_status(kw.get("request_id", "")),
    "plan_review":     lambda **kw: handle_plan_review(kw["request_id"], kw["approve"], kw.get("feedback", "")),
}

ALL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Run a shell command.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to run."}
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read file contents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path relative to the workspace root."},
                    "limit": {"type": "integer", "description": "Optional max number of lines to read."},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path relative to the workspace root."},
                    "content": {"type": "string", "description": "File content to write."},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace exact text in file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path relative to the workspace root."},
                    "old_text": {"type": "string", "description": "Exact text to replace."},
                    "new_text": {"type": "string", "description": "Replacement text."},
                },
                "required": ["path", "old_text", "new_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "todo",
            "description": "Update the task list and track progress for multi-step tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "description": "The full todo list to replace the current list.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Unique task id."},
                                "text": {"type": "string", "description": "Task description."},
                                "status": {
                                    "type": "string",
                                    "description": "Task status: pending, in_progress, or completed.",
                                    "enum": ["pending", "in_progress", "completed"],
                                },
                            },
                            "required": ["text"],
                        },
                    }
                },
                "required": ["items"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "load_skill",
            "description": "Load specialized knowledge by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Skill name to load",
                    }
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "task_create",
            "description": "Create a new task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "Task subject.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional task description.",
                    },
                },
                "required": ["subject"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "task_update",
            "description": "Update a task's status or dependencies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "Task id.",
                    },
                    "status": {
                        "type": "string",
                        "description": "New task status.",
                        "enum": ["pending", "in_progress", "completed"],
                    },
                    "addBlockedBy": {
                        "type": "array",
                        "description": "Task ids to add to blockedBy.",
                        "items": {"type": "integer"},
                    },
                    "removeBlockedBy": {
                        "type": "array",
                        "description": "Task ids to remove from blockedBy.",
                        "items": {"type": "integer"},
                    },
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "task_list",
            "description": "List all tasks with status summary.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "task_get",
            "description": "Get full details of a task by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "Task id.",
                    }
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "background_run",
            "description": "Run command in background thread. Returns task_id immediately.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to run in the background.",
                    }
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "background_check",
            "description": "Check background task status. Omit task_id to list all.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Optional background task id.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_message",
            "description": "Send a message to a teammate's inbox",
            "parameters": {
                "type": "object",
                "properties": {
                    "sender": {"type": "string", "description": "Sender teammate name."},
                    "to": {"type": "string", "description": "Receiver teammate name."},
                    "content": {"type": "string"},
                    "msg_type": {
                        "type": "string",
                        "enum": list(VALID_MSG_TYPES),
                    },
                },
                "required": ["sender", "to", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_inbox",
            "description": "Read and drain the lead's inbox.",
            "parameters": {
                "type": "object",
                "properties": {
                     "name": {
                        "type": "string",
                        "description": "Teammate name.",
                    },
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "broadcast",
            "description": "Send a message to all teammates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sender": {"type": "string", "description": "Sender teammate name."},
                    "content": {
                        "type": "string",
                        "description": "Message content to broadcast.",
                    },
                    "teammates": {
                        "type": "array",
                        "description": "List of teammate names to broadcast to.",
                        "items": {"type": "string"},
                    },
                },
                "required": ["sender", "content", "teammates"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "spawn_teammate",
            "description": "Spawn a persistent teammate that runs in its own thread.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Teammate name.",
                    },
                    "role": {
                        "type": "string",
                        "description": "Teammate role.",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Initial task prompt for the teammate.",
                    },
                },
                "required": ["name", "role", "prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_teammates",
            "description": "List all teammates with name, role, status.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "shutdown_response",
            "description": "Respond to a shutdown request. Approve to shut down, reject to keep working.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sender": {"type": "string", "description": "Sender teammate name."},
                    "request_id": {
                        "type": "string",
                        "description": "Shutdown request id.",
                    },
                    "approve": {
                        "type": "boolean",
                        "description": "Whether to approve the shutdown request.",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Optional reason for the shutdown request.",
                    },
                },
                "required": ["sender", "request_id", "approve"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "plan_approval",
            "description": "Submit a plan for lead approval. Provide plan text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sender": {"type": "string", "description": "Sender teammate name."},
                    "plan_text": {
                        "type": "string",
                        "description": "Plan text to submit.",
                    },
                },
                "required": ["sender", "plan_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "shutdown_request",
            "description": "Request a teammate to shut down gracefully. Returns a request_id for tracking.",
            "parameters": {
                "type": "object",
                "properties": {
                    "teammate": {"type": "string", "description": "Teammate name."},
                },
                "required": ["teammate"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_shutdown_status",
            "description": "Check the status of a shutdown request by request_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "request_id": {"type": "string", "description": "Shutdown request id."},
                },
                "required": ["request_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "plan_review",
            "description": "Approve or reject a teammate's plan. Provide request_id + approve + optional feedback.",
            "parameters": {
                "type": "object",
                "properties": {
                    "request_id": {"type": "string", "description": "Plan request id."},
                    "approve": {
                        "type": "boolean",
                        "description": "Whether to approve the plan.",
                    },
                    "feedback": {
                        "type": "string",
                        "description": "Optional feedback for the plan.",
                    },
                },
                "required": ["request_id", "approve"],
            },
        },
    },
]


TOOL_PROFILES = {
    "lead": [
        "bash",
        "read_file",
        "write_file",
        "edit_file",
        "send_message",
        "read_inbox",
        "broadcast",
        "spawn_teammate",
        "list_teammates",
        "shutdown_request",
        "check_shutdown_status",
        "plan_review",
    ],
    "teammate": [
        "bash",
        "read_file",
        "write_file",
        "edit_file",
        "send_message",
        "read_inbox",
        "shutdown_response",
        "plan_approval",
    ],
    "subagent": [
        "bash",
        "read_file",
        "write_file",
        "edit_file",
        "todo",
        "load_skill",
        "task_create",
        "task_update",
        "task_list",
        "task_get",
        "background_run",
        "background_check",
    ],
}


def _tool_name(schema: dict) -> str:
    return schema["function"]["name"]


def get_tool_names(profile: str) -> list[str]:
    names = TOOL_PROFILES.get(profile)
    if names is None:
        raise ValueError(
            f"Unknown tool profile '{profile}'. Valid: {', '.join(sorted(TOOL_PROFILES))}"
        )
    return list(names)


def build_tools(profile: str) -> list[dict]:
    wanted = set(get_tool_names(profile))
    return [schema for schema in ALL_TOOLS if schema["function"]["name"] in wanted]


def build_tool_handlers(profile: str) -> dict:
    return {name: ALL_TOOL_HANDLERS[name] for name in get_tool_names(profile)}


LEAD_TOOLS = build_tools("lead")
LEAD_TOOL_HANDLERS = build_tool_handlers("lead")
TEAMMATE_TOOLS = build_tools("teammate")
TEAMMATE_TOOL_HANDLERS = build_tool_handlers("teammate")
SUBAGENT_TOOLS = build_tools("subagent")
SUBAGENT_TOOL_HANDLERS = build_tool_handlers("subagent")

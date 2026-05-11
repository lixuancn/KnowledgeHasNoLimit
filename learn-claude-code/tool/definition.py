import json
from tool.tool_base import run_bash, run_read, run_write, run_edit
from constant import SKILLS_DIR, TASKS_DIR, INBOX_DIR, TEAM_DIR, VALID_MSG_TYPES



ALL_TOOL_HANDLERS = {
    "bash":             lambda **kw: run_bash(kw["command"]),
    "read_file":        lambda **kw: run_read(kw["path"], kw.get("limit")),
    "write_file":       lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file":        lambda **kw: run_edit(kw["path"], kw["old_text"], kw["new_text"]),
    "todo_write":       lambda **kw: TodoManage.update(kw["items"]),
    "task":             lambda **kw: run_subagent(kw["prompt"], kw.get("agent_type", "Explore")),
    "load_skill":       lambda **kw: SkillLoade.load(kw["name"]),
    "compress":         lambda **kw: "Compressing...",
    "background_run":   lambda **kw: BackgroundManage.run(kw["command"], kw.get("timeout", 120)),
    "background_check": lambda **kw: BackgroundManage.check(kw.get("task_id")),
    "task_create":      lambda **kw: TaskManage.create(kw["subject"], kw.get("description", "")),
    "task_get":         lambda **kw: TaskManage.get(kw["task_id"]),
    "task_update":      lambda **kw: TaskManage.update(kw["task_id"], kw.get("status"), kw.get("add_blocked_by"), kw.get("remove_blocked_by")),
    "task_list":        lambda **kw: TaskManage.list_all(),
    "spawn_teammate":   lambda **kw: TeammateManage.spawn(kw["name"], kw["role"], kw["prompt"]),
    "list_teammates":   lambda **kw: TeammateManage.list_all(),
    "send_message":     lambda **kw: MessageBus.send(kw["sender"], kw["to"], kw["content"], kw.get("msg_type", "message")),
    "read_inbox":       lambda **kw: json.dumps(MessageBus.read_inbox(kw["name"]), indent=2),
    "broadcast":        lambda **kw: MessageBus.broadcast(kw["sender"], kw["content"], TeammateManage.member_names()),
    "shutdown_request": lambda **kw: TeammateManage.handle_shutdown_request(kw["teammate"]),
    "plan_review":      lambda **kw: TeammateManage.handle_plan_review(kw["request_id"], kw["approve"], kw.get("feedback", "")),
    "claim_task":       lambda **kw: TaskManage.claim(kw["task_id"], kw["owner"]),
    "idle":             lambda **kw: "'Lead' does not idle. 'non-idea' supports idle, idle is Signal no more work",
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
            "name": "todo_write",
            "description": "Replace the todo list with validated todo items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "description": "The full todo list to replace the current list.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string", "description": "Todo content."},
                                "status": {
                                    "type": "string",
                                    "description": "Todo status.",
                                    "enum": ["pending", "in_progress", "completed"],
                                },
                                "activeForm": {
                                    "type": "string",
                                    "description": "Active form of the todo item.",
                                },
                            },
                            "required": ["content", "activeForm"],
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
            "name": "task",
            "description": "Run a subagent with a prompt and optional agent type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Prompt for the subagent.",
                    },
                    "agent_type": {
                        "type": "string",
                        "description": "Optional subagent type.",
                    },
                },
                "required": ["prompt"],
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
            "name": "compress",
            "description": "Manually compress conversation context.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
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
            "name": "task_get",
            "description": "Get full details of a task by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "Task id.",
                    },
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "task_update",
            "description": "Update task status or dependency links.",
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
                    "add_blocked_by": {
                        "type": "integer",
                        "description": "Task id to add as a blocker.",
                    },
                    "remove_blocked_by": {
                        "type": "integer",
                        "description": "Task id to remove from blockers.",
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
                "required": [],
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
                "properties": {
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_message",
            "description": "Send a message to a teammate's inbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sender": {"type": "string", "description": "Sender teammate name."},
                    "to": {"type": "string", "description": "Receiver teammate name."},
                    "content": {"type": "string", "description": "Message content."},
                    "msg_type": {
                        "type": "string",
                        "description": "Optional message type.",
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
            "name": "background_run",
            "description": "Run command in background thread. Returns task_id immediately.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to run in the background.",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Optional timeout in seconds.",
                    },
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
            "name": "read_inbox",
            "description": "Read and drain a teammate inbox.",
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
            "description": "Send a message to all teammates known by the team manager.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sender": {"type": "string", "description": "Sender teammate name."},
                    "content": {
                        "type": "string",
                        "description": "Message content to broadcast.",
                    },
                },
                "required": ["sender", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "shutdown_request",
            "description": "Request a teammate to shut down gracefully.",
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
            "name": "plan_review",
            "description": "Approve or reject a teammate plan.",
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
    {
        "type": "function",
        "function": {
            "name": "claim_task",
            "description": "Claim a task from the task board by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "Task id."},
                    "owner": {"type": "string", "description": "Task owner."},
                },
                "required": ["task_id", "owner"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "idle",
            "description": "Signal that you have no more work. Enters idle polling phase.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

def getToolListForLead() -> list[str]:
    toolList = [
        "bash",
        "read_file",
        "write_file",
        "edit_file",
        "todo_write",
        "load_skill",
        "compress",
        "spawn_teammate",
        "list_teammates",
        "background_run",
        "background_check",
        "task_create",
        "task_update",
        "task_list",
        "task_get",
        "send_message",
        "read_inbox",
        "broadcast",
        "shutdown_request",
        "plan_review",
        "idle",
        "claim_task",
    ]
    return toolList

def getToolListForSubAgent(agent_type: str) -> list[str]:
    toolList = ["bash","read_file",]
    if agent_type != "Explore":
        toolList += ["write_file", "edit_file"]
    return toolList

def getToolListForTeammate() -> list[str]:
    toolList = [
        "bash",
        "read_file",
        "write_file",
        "edit_file",
        "send_message",
        "idle",
        "claim_task",
    ]
    return toolList

def get_tool_names(profile: str, agent_type: str = "Explore") -> list[str]:
    names = []
    if profile == "lead":
        names = getToolListForLead()
    elif profile == "teammate":
        names = getToolListForTeammate()
    elif profile == "subagent":
        names = getToolListForSubAgent(agent_type)
    else:
        raise ValueError(f"Unknown tool profile '{profile}'")
    return list(names)

def build_tools(profile: str, agent_type: str = "Explore") -> list[dict]:
    wanted = set(get_tool_names(profile, agent_type))
    return [schema for schema in ALL_TOOLS if schema["function"]["name"] in wanted]

def build_tool_handlers(profile: str, agent_type: str = "Explore") -> dict:
    return {name: ALL_TOOL_HANDLERS[name] for name in get_tool_names(profile, agent_type)}

# 工具定义 ------------
# 主A 工具定义
def get_lead_tools() -> list[dict]:
    return build_tools("lead")

def get_lead_tool_handlers() -> dict:
    return build_tool_handlers("lead")

# 主A派生子A 工具定义
def get_subagent_tools() -> list[dict]:
    return build_tools("subagent")

def get_subagent_tool_handlers() -> dict:
    return build_tool_handlers("subagent", agent_type="Explore")

# 队友 工具定义
def get_teammate_tools() -> list[dict]:
    return build_tools("teammate")

def get_teammate_tool_handlers() -> dict:
    return build_tool_handlers("teammate")

# 工具类初始化-----------
def getTodoManager():
    from tool.tool_todomanager import TodoManager
    return TodoManager
TodoManage = getTodoManager()()

def getSkillLoader():
    from tool.tool_skill import SkillLoader
    return SkillLoader
SkillLoade = getSkillLoader()(SKILLS_DIR)

def getTaskManager():
    from tool.tool_taskmanager import TaskManager
    return TaskManager
TaskManage = getTaskManager()(TASKS_DIR)

def getBackgroundManager():
    from tool.tool_background import BackgroundManager
    return BackgroundManager
BackgroundManage = getBackgroundManager()()

def getMessageBus():
    from tool.tool_messagebuser import MessageBuser
    return MessageBuser
MessageBus = getMessageBus()(INBOX_DIR)

def getTeammateManage():
    from tool.tool_teammatemanager import TeammateManager
    return TeammateManager
TeammateManage = getTeammateManage()(TEAM_DIR, MessageBus, TaskManage, get_teammate_tools(), get_teammate_tool_handlers())

def getRunSubagent():
    from tool.tool_subagent import run_subagent
    return run_subagent
run_subagent = getRunSubagent()
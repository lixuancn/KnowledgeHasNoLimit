from pathlib import Path


WORKDIR = Path.cwd()
SKILLS_DIR = WORKDIR / "skills"

TODO_REMINDER = "<reminder>Update your todos.</reminder>"

ENABLE_COMPACT = False
THRESHOLD = 50000
TRANSCRIPT_DIR = WORKDIR / ".transcripts"
KEEP_RECENT = 3
PRESERVE_RESULT_TOOLS = {"read_file"}

TASKS_DIR = WORKDIR / ".tasks"

VALID_MSG_TYPES = {
    "message",
    "broadcast",
    "shutdown_request",
    "shutdown_response",
    "plan_approval_response",
}

TEAM_DIR = WORKDIR / ".team"
INBOX_DIR = TEAM_DIR / "inbox"
TASKS_DIR = WORKDIR / ".tasks"

POLL_INTERVAL = 5
IDLE_TIMEOUT = 60
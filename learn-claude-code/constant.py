from pathlib import Path

VALID_MSG_TYPES = {
    "message",
    "broadcast",
    "shutdown_request",
    "shutdown_response",
    "plan_approval_response",
}

WORKDIR = Path.cwd()
TEAM_DIR = WORKDIR / ".team"
INBOX_DIR = TEAM_DIR / "inbox"
TASKS_DIR = WORKDIR / ".tasks"
SKILLS_DIR = WORKDIR / "skills"
TRANSCRIPT_DIR = WORKDIR / ".transcripts"

TODO_REMINDER = "<reminder>Update your todos.</reminder>"

ENABLE_COMPACT = False
THRESHOLD = 50000
KEEP_RECENT = 3
PRESERVE_RESULT_TOOLS = {"read_file"}



TOKEN_THRESHOLD = 100000
POLL_INTERVAL = 5
IDLE_TIMEOUT = 60

POLL_INTERVAL = 5
IDLE_TIMEOUT = 60
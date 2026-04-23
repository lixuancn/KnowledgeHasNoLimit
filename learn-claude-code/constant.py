from pathlib import Path


WORKDIR = Path.cwd()
SKILLS_DIR = WORKDIR / "skills"

TODO_REMINDER = "<reminder>Update your todos.</reminder>"

THRESHOLD = 50000
TRANSCRIPT_DIR = WORKDIR / ".transcripts"
KEEP_RECENT = 3
PRESERVE_RESULT_TOOLS = {"read_file"}
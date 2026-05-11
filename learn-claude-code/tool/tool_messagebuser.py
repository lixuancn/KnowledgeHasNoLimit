from pathlib import Path
import time
import json
from constant import VALID_MSG_TYPES

class MessageBuser:
    def __init__(self, inbox_dir: Path):
        self.dir = inbox_dir
        self.dir.mkdir(parents=True, exist_ok=True)
    
    def _normalize_name(self, name: str) -> str:
        return name.strip().casefold()
    
    def _inbox_path(self, name: str) -> Path:
        return self.dir / f"{self._normalize_name(name)}.jsonl"

    def send(self, sender: str, to: str, content: str, msg_type: str = "message", extra: dict = None) -> str:
        sender = self._normalize_name(sender)
        to = self._normalize_name(to)
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
        with open(self._inbox_path(to), "a") as f:
            f.write(json.dumps(msg) + "\n")
        return f"Sent {msg_type} to {to}"

    def read_inbox(self, name: str) -> list:
        name = self._normalize_name(name)
        path = self._inbox_path(name)
        if not path.exists(): 
            return []
        msgs = [json.loads(l) for l in path.read_text().strip().splitlines() if l]
        path.write_text("")
        return msgs

    def broadcast(self, sender: str, content: str, names: list) -> str:
        count = 0
        for n in names:
            name = self._normalize_name(n)
            if name != sender:
                self.send(sender, name, content, "broadcast")
                count += 1
        return f"Broadcast to {count} teammates"
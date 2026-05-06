"""Regression tests for teammate name normalization."""

import importlib
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


class _FakeChatClient:
    def bind_tools(self, *_args, **_kwargs):
        return self

    def bind(self, *_args, **_kwargs):
        return self


class _FakeLLM:
    def ChatOpenAI(self):
        return _FakeChatClient()


class _FakeMessage:
    def __init__(self, content=None, **kwargs):
        self.content = content
        self.kwargs = kwargs


class _FakeThread:
    def __init__(self, target=None, args=(), daemon=None):
        self.target = target
        self.args = args
        self.daemon = daemon
        self.started = False

    def start(self):
        self.started = True

    def is_alive(self):
        return False


def _import_agent_teams():
    fake_tool_module = types.ModuleType("tool")
    fake_tool_module.TEAMMATE_TOOLS = []
    fake_tool_module.TEAMMATE_TOOL_HANDLERS = {}

    fake_llm_module = types.ModuleType("llm")
    fake_llm_module.LLM = lambda: _FakeLLM()

    fake_langchain_core = types.ModuleType("langchain_core")
    fake_langchain_messages = types.ModuleType("langchain_core.messages")
    fake_langchain_messages.HumanMessage = _FakeMessage
    fake_langchain_messages.SystemMessage = _FakeMessage
    fake_langchain_messages.ToolMessage = _FakeMessage
    fake_langchain_core.messages = fake_langchain_messages

    sys.modules.pop("agent_teams", None)
    with patch.dict(
        sys.modules,
        {
            "tool": fake_tool_module,
            "llm": fake_llm_module,
            "langchain_core": fake_langchain_core,
            "langchain_core.messages": fake_langchain_messages,
        },
    ):
        return importlib.import_module("agent_teams")


class TestAgentTeams(unittest.TestCase):
    def test_spawn_treats_name_case_insensitively(self):
        agent_teams = _import_agent_teams()

        with tempfile.TemporaryDirectory() as tmpdir, patch.object(
            agent_teams.threading,
            "Thread",
            _FakeThread,
        ):
            manager = agent_teams.TeammateManager(Path(tmpdir) / ".team")

            manager.spawn("Alice", "developer", "first task")
            manager.spawn("alice", "reviewer", "second task")

            self.assertEqual(len(manager.config["members"]), 1)
            self.assertEqual(manager.config["members"][0]["name"], "Alice")
            self.assertEqual(manager.config["members"][0]["role"], "reviewer")
            self.assertEqual(set(manager.threads.keys()), {"alice"})

    def test_message_bus_reuses_inbox_across_name_casing(self):
        agent_teams = _import_agent_teams()

        with tempfile.TemporaryDirectory() as tmpdir:
            bus = agent_teams.MessageBuser(Path(tmpdir) / "inbox")

            bus.send("lead", "Alice", "hello")

            messages = bus.read_inbox("alice")

            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0]["from"], "lead")
            self.assertEqual(messages[0]["content"], "hello")
            self.assertEqual(bus.read_inbox("ALICE"), [])


if __name__ == "__main__":
    unittest.main()

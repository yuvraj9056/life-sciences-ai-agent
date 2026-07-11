import os
import json
import tempfile
import unittest
from unittest.mock import MagicMock, patch


# We import the module but patch graph before it is used.
import final_response


class TestFinalResponseMemory(unittest.TestCase):
    def test_disk_memory_roundtrip_and_threading(self):
        with tempfile.TemporaryDirectory() as td:
            mem_path = os.path.join(td, "chat_memory.json")
            cfg = final_response.MemoryConfig(memory_path=mem_path, max_turns=2, summary_trigger_turns=3)
            memory = final_response.DiskChatMemory(cfg)

            tid1 = "patientA"
            tid2 = "patientB"

            memory.append(tid1, "user", "Q1")
            memory.append(tid1, "assistant", "A1")
            memory.append(tid2, "user", "Q2")

            # Reload from disk by constructing again
            memory2 = final_response.DiskChatMemory(cfg)
            self.assertEqual(len(memory2.get_messages(tid1)), 2)
            self.assertEqual(memory2.get_messages(tid1)[0]["content"], "Q1")
            self.assertEqual(len(memory2.get_messages(tid2)), 1)
            self.assertEqual(memory2.get_messages(tid2)[0]["content"], "Q2")

    def test_build_effective_question_uses_recent_history(self):
        with tempfile.TemporaryDirectory() as td:
            mem_path = os.path.join(td, "chat_memory.json")
            cfg = final_response.MemoryConfig(memory_path=mem_path, max_turns=2, summary_trigger_turns=10)
            memory = final_response.DiskChatMemory(cfg)
            tid = "t"

            memory.append(tid, "user", "How many patients?")
            memory.append(tid, "assistant", "There are X")
            memory.append(tid, "user", "And for diabetes?")

            effective, dbg = final_response._build_effective_question(
                question="And for diabetes?",
                memory=memory,
                thread_id=tid,
                cfg=cfg,
            )

            self.assertIn("User: How many patients?", effective)
            self.assertIn("Assistant: There are X", effective)
            self.assertIn("Current user question", effective)
            self.assertEqual(dbg["thread_id"], "t")
            self.assertEqual(dbg["summary_used"], "false")


class TestFinalResponseIntegration(unittest.TestCase):
    def test_cli_single_turn_calls_graph_with_effective_question(self):
        # This test doesn't import langgraph; it patches graph.invoke.
        with tempfile.TemporaryDirectory() as td:
            mem_path = os.path.join(td, "chat_memory.json")
            cfg = final_response.MemoryConfig(memory_path=mem_path, max_turns=2, summary_trigger_turns=10)
            memory = final_response.DiskChatMemory(cfg)
            tid = "threadX"

            # fake graph.invoke output
            fake_graph = MagicMock()
            fake_graph.invoke.return_value = {"answer": "FAKE_ANSWER"}

            with patch.object(final_response, "graph", fake_graph):
                memory.append(tid, "user", "Q")
                effective_question, _dbg = final_response._build_effective_question(
                    question="Q",
                    memory=memory,
                    thread_id=tid,
                    cfg=cfg,
                )

                resp = final_response.graph.invoke({"question": effective_question})
                self.assertEqual(resp["answer"], "FAKE_ANSWER")
                fake_graph.invoke.assert_called_once()


if __name__ == "__main__":
    unittest.main()


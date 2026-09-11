import importlib.util
from pathlib import Path
import tempfile
import unittest
spec = importlib.util.spec_from_file_location("bridge", Path(__file__).parents[1]/"scripts/claude_bridge.py")
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

class BridgeTests(unittest.TestCase):
    def test_invalid_packet_shapes(self):
        for packet in ([], None, "text", {}):
            with self.assertRaises(ValueError):
                bridge.prepare(packet)

    def test_scope_and_no_shell(self):
        with tempfile.TemporaryDirectory(prefix="Randall space ") as home:
            packet = dict(classification="public", cloud_approved=True,
                          customizations_reviewed=True, workspace=home,
                          model="sonnet", max_budget_usd=0.5, brief="Review synthetic VLAN example")
            command, prompt, workspace, timeout = bridge.prepare(packet)
            self.assertIn("dontAsk",command)
            self.assertEqual(command[command.index("--tools")+1],"")
            self.assertNotIn(packet["brief"],command)
            self.assertEqual(str(workspace),home)
            for key,value in (("cloud_approved",False),("classification","local-only"),
                              ("max_turns",100),("customizations_reviewed",False)):
                with self.assertRaises(ValueError):
                    bridge.prepare({**packet,key:value})

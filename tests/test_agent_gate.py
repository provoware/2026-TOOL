from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("provoware_agent_gate", ROOT / "scripts/agent_gate.py")
agent_gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_gate)


class AgentGateTests(unittest.TestCase):
    def test_static_ui_change_is_r1(self):
        risk, _ = agent_gate.risk_level(["app/static/css/design.css"], [])
        self.assertEqual(risk, "R1")

    def test_persistence_or_agent_contract_change_is_r3(self):
        for path in ("app/data_core.py", "app/self_repair.py", "AGENTS.md", ".agents/RISIKO_AGENT.md"):
            with self.subTest(path=path):
                risk, _ = agent_gate.risk_level([path], [])
                self.assertEqual(risk, "R3")

    def test_deleting_test_or_quality_contract_is_r4(self):
        for path in ("tests/test_data_core.py", "scripts/validate_all.sh", ".agents/PLAN_PRUEFER.md", "projekt-manifest.json"):
            with self.subTest(path=path):
                risk, _ = agent_gate.risk_level([path], [path])
                self.assertEqual(risk, "R4")


if __name__ == "__main__":
    unittest.main()

import unittest

from faang_agent import FaangSeniorAgent, _resolve_task


class TestFaangSeniorAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = FaangSeniorAgent()

    def test_email_mode(self) -> None:
        response = self.agent.run("Ответь клиенту", mode="email")
        self.assertEqual(response.mode, "email")
        self.assertIn("Здравствуйте", response.output)

    def test_code_mode_contains_python_block(self) -> None:
        response = self.agent.run("Напиши кэш", mode="code")
        self.assertEqual(response.mode, "code")
        self.assertIn("```python", response.output)
        self.assertIn("maxsize", response.output)

    def test_analysis_mode_mentions_project_state(self) -> None:
        response = self.agent.run("Проанализируй проект", mode="analysis")
        self.assertEqual(response.mode, "analysis")
        self.assertIn("состояние проекта", response.context)

    def test_auto_mode_detects_email(self) -> None:
        response = self.agent.run("Ответь на письмо клиенту про баг")
        self.assertEqual(response.mode, "email")

    def test_auto_mode_detects_code(self) -> None:
        response = self.agent.run("Напиши python функцию для API")
        self.assertEqual(response.mode, "code")

    def test_resolve_task_uses_direct_task(self) -> None:
        args = type("Args", (), {"task": "x", "interactive": False})
        self.assertEqual(_resolve_task(args), "x")


if __name__ == "__main__":
    unittest.main()

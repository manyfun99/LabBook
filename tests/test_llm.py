import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from labbook import llm

SCHEMA = {"type": "object", "properties": {"a": {"type": "integer"}}, "required": ["a"]}


def ok(structured, model="claude-opus-5-5"):
    body = {"type": "result", "subtype": "success", "is_error": False, "structured_output": structured,
            "modelUsage": {model: {"inputTokens": 1}}}
    return subprocess.CompletedProcess([], 0, stdout=json.dumps(body), stderr="")


class Runner:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, args, **kwargs):
        self.calls.append((args, kwargs))
        r = self.responses.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


class RunClaudeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = Path(self.tmp.name) / "llm"

    def tearDown(self):
        self.tmp.cleanup()

    def call(self, runner, **kw):
        return llm.run_claude("프롬프트", SCHEMA, "opus", runner=runner, cwd=self.cwd, **kw)

    def test_구조화_출력과_실제_모델명을_돌려준다(self):
        out, model = self.call(Runner(ok({"a": 1})))
        self.assertEqual(out, {"a": 1})
        self.assertEqual(model, "claude-opus-5-5")

    def test_modelUsage에_보조_모델이_섞여도_요청한_모델을_기록한다(self):
        body = {"is_error": False, "structured_output": {"a": 1},
                "modelUsage": {"claude-haiku-4-5": {"outputTokens": 900}, "claude-opus-5-5": {"outputTokens": 50}}}
        runner = Runner(subprocess.CompletedProcess([], 0, stdout=json.dumps(body), stderr=""))
        self.assertEqual(self.call(runner)[1], "claude-opus-5-5")

    def test_별칭과_맞는_키가_없으면_출력_토큰이_가장_많은_모델(self):
        body = {"is_error": False, "structured_output": {"a": 1},
                "modelUsage": {"x-small": {"outputTokens": 5}, "x-large": {"outputTokens": 50}}}
        runner = Runner(subprocess.CompletedProcess([], 0, stdout=json.dumps(body), stderr=""))
        self.assertEqual(self.call(runner)[1], "x-large")

    def test_도구_없이_세션을_남기지_않고_격리된_cwd에서_호출한다(self):
        runner = Runner(ok({"a": 1}))
        self.call(runner)
        args, kwargs = runner.calls[0]
        self.assertEqual(args[:2], ["claude", "-p"])
        self.assertEqual(args[args.index("--tools") + 1], "")
        self.assertIn("--no-session-persistence", args)
        self.assertEqual(args[args.index("--model") + 1], "opus")
        self.assertEqual(json.loads(args[args.index("--json-schema") + 1]), SCHEMA)
        self.assertEqual(kwargs["input"], "프롬프트")
        self.assertEqual(kwargs["cwd"], self.cwd)
        self.assertEqual(kwargs["timeout"], 600)
        self.assertTrue(self.cwd.is_dir())

    def test_타임아웃이면_1회_재시도한다(self):
        runner = Runner(subprocess.TimeoutExpired("claude", 600), ok({"a": 2}))
        self.assertEqual(self.call(runner)[0], {"a": 2})
        self.assertEqual(len(runner.calls), 2)

    def test_비정상_종료면_1회_재시도한다(self):
        runner = Runner(subprocess.CompletedProcess([], 1, stdout="", stderr="boom"), ok({"a": 3}))
        self.assertEqual(self.call(runner)[0], {"a": 3})

    def test_is_error나_구조화_출력_누락도_실패로_본다(self):
        bad = subprocess.CompletedProcess([], 0, stdout=json.dumps({"is_error": True, "result": "x"}), stderr="")
        missing = subprocess.CompletedProcess([], 0, stdout=json.dumps({"is_error": False}), stderr="")
        with self.assertRaises(llm.LLMError):
            self.call(Runner(bad, missing))

    def test_JSON이_아니면_실패로_본다(self):
        garbage = subprocess.CompletedProcess([], 0, stdout="not json", stderr="")
        self.assertEqual(self.call(Runner(garbage, ok({"a": 4})))[0], {"a": 4})

    def test_검증_콜백이_실패하면_재시도하고_두번_실패하면_LLMError(self):
        def validate(out):
            if out["a"] < 10:
                raise ValueError("작다")

        self.assertEqual(self.call(Runner(ok({"a": 1}), ok({"a": 11})), validate=validate)[0], {"a": 11})
        with self.assertRaises(llm.LLMError):
            self.call(Runner(ok({"a": 1}), ok({"a": 2})), validate=validate)


if __name__ == "__main__":
    unittest.main()

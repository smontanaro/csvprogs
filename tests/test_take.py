import subprocess
import sys

from tests import SPY_CSV


def test_cli():
    with open(SPY_CSV, "r", encoding="utf-8") as csvf:
        lines = [line.strip() for line in csvf]
        raw = bytes("\n".join(lines), encoding="utf-8")
        result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.take",
                                "-n", "3"],
            input=raw,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        assert result.returncode == 0
        outlines = result.stdout.strip().split(b"\n")
        assert len(outlines) == (len(lines) + 1) // 3

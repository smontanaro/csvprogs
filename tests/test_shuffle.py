import subprocess

from tests import SPY_CSV


def test_cli():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.shuffle",
        SPY_CSV],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode == 0

    with open(SPY_CSV, encoding="utf-8") as inf:
        output = result.stdout.decode("utf-8")
        input = inf.read()
        assert (len(output.split("\n")) == len(input.split("\n")) and
                output != input and
                sorted(output.split("\n")) == sorted(input.split("\n")))

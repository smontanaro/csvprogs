import subprocess

from tests import VRTX_DAILY

EPS = 1e-7


def test_cli():
    with open(VRTX_DAILY, "rb") as vrtx:
        vrtx_data = vrtx.read()

    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.mean",
        "-f", "% Change-VRTX", "-m", "-10", "-M", "+10"],
        stdout=subprocess.PIPE, stderr=None, input=vrtx_data)
    assert result.returncode == 0
    act = [float(v) for v in result.stdout.decode("utf-8").split(",")]
    exp = [3845.0, 0.043686, 0.049400, 2.0958242]
    delta = [abs(x-y) for (x, y) in zip(act, exp)]
    assert max(delta) <= EPS, (exp, act, delta)

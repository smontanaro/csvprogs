#!/usr/bin/env python

import subprocess

def test_bad_cli():
    result = subprocess.run(["./venv/bin/python", "-m", "csvprogs.csvmerge",
        "-k", "date,time"], stdout=subprocess.PIPE, stderr=None)
    assert result.returncode != 0

if __name__ == "__main__":
    unittest.main()

import json
import os
import tempfile
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from ieuler.client import Client


@pytest.fixture
def problems():
    with open(os.path.join(os.path.dirname(__file__), '.problems'), 'rt') as f:
        return json.load(f)


@pytest.fixture
def solved_problem_4():
    return {
        "ID": 4,
        "code": {
            "python3": {
                "filecontent": "\"\"\"{\n    \"Description / Title\": \"Largest palindrome product\",\n    \"ID\": 4,\n    \"Problem\": \"<div class=\\\"problem_content\\\" role=\\\"problem\\\">\\n<p>A palindromic number reads the same both ways. The largest palindrome made from the product of two 2-digit numbers is 9009 = 91 \\u00d7 99.</p>\\n<p>Find the largest palindrome made from the product of two 3-digit numbers.</p>\\n</div>\",\n    \"page_url\": \"https://projecteuler.net/archives\",\n    \"problem_url\": \"https://projecteuler.net/problem=4\"\n}\n\n\"\"\"\n\n\ndef answer():\n    \"\"\" Solve the problem here! Make sure to return the answer. \"\"\"\n    return 0\n\n\nif __name__ == \"__main__\":\n    \"\"\" Below is OK to leave alone \"\"\"\n    print(answer())\n",
                "filename": "4.py",
                "submission": None
            }
        },
    }


@pytest.fixture
def default_client(problems, solved_problem_4):
    d = [tempfile.mkstemp() for _ in range(0, 4)]  # make 4 temp files
    client = Client(cookies_filename=d[0][1],
                    credentials_filename=d[1][1],
                    problems_filename=d[2][1],
                    default_language_filename=d[3][1])
    ping_ipe = client.ping_ipe
    get_all_problems = client.get_all_problems
    get_from_ipe = client.get_from_ipe

    client.ping_ipe = MagicMock(return_value=None)
    client.get_all_problems = MagicMock(return_value=problems)
    client.get_from_ipe = MagicMock(return_value=[solved_problem_4])

    yield client

    client.ping_ipe = ping_ipe
    client.get_all_problems = get_all_problems
    client.get_from_ipe = get_from_ipe
    for _ in d:
        os.close(_[0])
        os.unlink(_[1])


@pytest.fixture
def default_session(default_client):
    class Session(object):
        def __init__(self):
            self.client = default_client

    yield Session()


@pytest.fixture
def runner():
    return CliRunner()

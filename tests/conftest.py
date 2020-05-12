import json
import os
import tempfile

import pytest
from click.testing import CliRunner

from ieuler.client import Client


@pytest.fixture
def default_client():
    d = [tempfile.mkstemp() for _ in range(0, 4)]  # make 4 temp files
    yield Client(cookies_filename=d[0][1],
                 credentials_filename=d[1][1],
                 problems_filename=d[2][1],
                 default_language_filename=d[3][1])
    for _ in d:
        os.close(_[0])
        os.unlink(_[1])


@pytest.fixture
def default_session(default_client):
    class Session(object):
        def __init__(self):
            self.client = default_client

    return Session()


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def problems():
    with open(os.path.join(os.path.dirname(__file__), '.problems'), 'rt') as f:
        return json.load(f)

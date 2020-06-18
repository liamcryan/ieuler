import json
import os

from ieuler.cli import ilr, fetch
from ieuler.language_templates import get_template


def test_default_client(default_client, problems):
    assert default_client.cookies_filename != '.cookies'
    assert default_client.credentials_filename != '.credentials'
    assert default_client.problems_filename != '.problems'
    assert default_client.default_language_filename != '.default_language'
    assert default_client.ping_ipe() is None
    assert default_client.get_all_problems() == problems


def test_default_session(default_session, default_client):
    assert default_session.client == default_client


def test_config(runner, default_session):
    result = runner.invoke(ilr, ['config'], obj=default_session)
    assert json.loads(result.output) == {
        "credentials": {},
        "language": "python3",
        "server": {
            "host": "127.0.0.1",
            "port": 2718
        }
    }
    result = runner.invoke(ilr, ['config', '-language', 'node'], obj=default_session)
    node_template = get_template('node')
    client_language_template = default_session.client.load_language_template()
    assert client_language_template.language == node_template.language
    assert client_language_template.extension == node_template.extension

    assert json.loads(result.output) == {
        "credentials": {},
        "language": "node",
        "server": {
            "host": "127.0.0.1",
            "port": 2718
        }
    }
    result = runner.invoke(ilr, ['config', '-host', 'ieuler.net', '-port', '80'], obj=default_session)
    assert os.environ['IEULER_SERVER_HOST'] == 'ieuler.net'
    assert os.environ['IEULER_SERVER_PORT'] == str(80)

    assert json.loads(result.output) == {
        "credentials": {},
        "language": "node",
        "server": {
            "host": "ieuler.net",
            "port": 80
        }
    }


def test_fetch(runner, default_session):
    result = runner.invoke(fetch, obj=default_session)

    # assert fetched problems are in order
    p = 1
    for _ in default_session.client.problems:
        assert _['ID'] == p
        p += 1

    # assert number 4 has code (see conftest)
    assert 'code' in default_session.client.problems[3]

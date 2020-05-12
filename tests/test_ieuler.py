import json

from ieuler.cli import ilr


def test_default_client(default_client):
    assert default_client.cookies_filename != '.cookies'
    assert default_client.credentials_filename != '.credentials'
    assert default_client.problems_filename != '.problems'
    assert default_client.default_language_filename != '.default_language'


def test_default_session(default_session, default_client):
    assert default_session.client == default_client


# todo: quite a bit to test here
#   ilr config -> can be viewed and changed
#   other ilr commands -> make sure the message to user makes sense
#   and solve and submit may have a lot of cases
def test_config(runner):
    result = runner.invoke(ilr, ['config'])

    assert json.loads(result.output) == {
        "credentials": {},
        "language": "python3",
        "server": {
            "host": "127.0.0.1",
            "port": 5000
        }
    }


def test_default_client(default_client):
    assert default_client.cookies_filename
    assert default_client.credentials_filename
    assert default_client.problems_filename
    assert default_client.language_template_filename

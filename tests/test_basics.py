from flask import current_app
import pytest


@pytest.mark.app(debug=False)
def test_app(app):
    assert not app.debug, 'Ensure the app not in debug mode'


def test_app_exist(app):
    assert current_app is not None


def test_app_is_testing(app):
    assert current_app.config['TESTING']

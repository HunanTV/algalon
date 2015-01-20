from app.models import User
import pytest


@pytest.fixture(scope='module')
def user():
    user = User(username='dq', email='dq@example.com')
    return user


def test_create_user(db, user):
    assert User.query.count() == 0
    db.session.add(user)
    db.session.commit()
    assert User.query.count() == 1


def test_delete_user(db, user):
    assert User.query.count() == 1
    db.session.delete(user)
    db.session.commit()
    assert User.query.count() == 0

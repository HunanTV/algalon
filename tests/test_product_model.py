from app.models import User, Project
import pytest


@pytest.fixture(scope="function")
def user(db):
    u = User.query.filter_by(username='test').first()
    if u is None:
        u = User(username='test', email='test@test.com')
        db.session.add(u)
        db.session.commit()
    return u


def test_create_project(db, user):
    p = Project(name='test_project')
    assert user.projects.count() == 0
    user.projects.append(p)
    db.session.add(user)
    db.session.commit()
    assert user.projects.count() == 1


def test_reset_token(db, user):
    p = user.projects.first()
    old_token = p.token
    p.reset_token()
    new_token = p.token
    assert old_token != new_token


def test_delete_project(db, user):
    assert user.projects.count() == 1
    p = user.projects.first()
    user.projects.remove(p)
    db.session.add(user)
    db.session.commit()
    assert user.projects.count() == 0

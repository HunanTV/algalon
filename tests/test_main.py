# coding=utf-8

from flask import url_for
from app.models import User, Project, ToEmail
import pytest
import json


@pytest.fixture(scope="function")
def user(db):
    u = User.query.filter_by(username='test').first()
    if u is None:
        u = User(username='test', email='test@test.com')
        p = Project(name='test_project')
        u.projects.append(p)
        db.session.add(u)
        db.session.commit()
    return u


def set_user_cookie(client, config, user):
    user_dict = {'username': user.username, 'email': user.email}
    client.set_cookie('localhost', config['OPENID2_PROFILE_COOKIE_NAME'], json.dumps(user_dict))


def test_index(client):
    response = client.get(url_for('main.index'))
    assert response.status_code == 200
    assert 'Stranger' in response.get_data(as_text=True)


def test_user(client, config, user):
    set_user_cookie(client, config, user)

    response = client.get(url_for('main.user',  username='wrong_test'), follow_redirects=True)
    assert response.status_code == 403

    response = client.get(url_for('main.user',  username='test'), follow_redirects=True)
    assert response.status_code == 200
    assert 'test' in response.get_data(as_text=True)
    assert 'test_project' in response.get_data(as_text=True)

    p = user.projects.first()
    token = p.token
    assert token in response.get_data(as_text=True)
    response = client.get(url_for('main.reset_token', username=user.username, project_name=p.name))
    assert token not in response.get_data(as_text=True)

    new_project_name = 'test2'
    assert new_project_name not in response.get_data(as_text=True)
    response = client.post(url_for('main.create_user_project', username=user.username),
                              data={'name': new_project_name},
                              follow_redirects=True)
    assert new_project_name in response.get_data(as_text=True)

    response = client.get(url_for('main.delete_project', username=user.username, project_name=new_project_name))
    assert new_project_name not in response.get_data(as_text=True)


def test_user_project(client, config, user):
    set_user_cookie(client, config, user)
    username = user.username
    project_name = user.projects.first().name
    response = client.get(url_for('main.user_project', username=username, project_name=project_name))
    assert u'应用程序: {0} 的报警信息'.format(project_name) in response.get_data(as_text=True)


def test_to_emails(client, config, user):
    set_user_cookie(client, config, user)
    username = user.username
    project_name = user.projects.first().name
    response = client.get(url_for('main.show_to_emails', username=username, project_name=project_name))
    assert u'接收报警邮件列表' in response.get_data(as_text=True)

    response = client.post(url_for('main.create_to_email', username=user.username, project_name=project_name),
                           data={'addresses': 'test@email.com, test1@email.com'},
                           follow_redirects=True)
    assert 'test@email.com' in response.get_data(as_text=True)
    assert 'test1@email.com' in response.get_data(as_text=True)

    to_email = ToEmail.query.filter_by(address='test1@email.com').first()
    response = client.get(url_for('main.delete_to_email', username=user.username, project_name=project_name, to_email_id=to_email.id))
    assert 'test1@email.com' not in response.get_data(as_text=True)

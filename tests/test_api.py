from flask import url_for
from urlparse import urlparse
from app.models import User, Project
import pytest
import json


def get_api_headers():
    return {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }


@pytest.fixture(scope="function")
def project(db):
    u = User.query.filter_by(username='test').first()
    if u is None:
        u = User(username='test', email='test@test.com')
        p = Project(name='test_project')
        u.projects.append(p)
        db.session.add(u)
        db.session.commit()
    return u.projects.first()


def test_register_dsn(client, config, project):
    username = project.owner.username
    project_name = project.name
    token = project.token
    host = config['ALGALON_SERVER_HOST']
    port = config['ALGALON_SERVER_PORT']
    hostname = urlparse(host).hostname
    path = urlparse(host).path
    dsn = 'http://{token}@{host}:{port}{path}'.format(
        token=token,
        host=hostname,
        port=port,
        path=path)

    resoponse = client.get(url_for('api.register_dsn', username=username, project_name=project_name))
    assert resoponse.status_code == 201
    assert dsn == resoponse.json['dsn']


def test_alarm(client, db, project):
    data = {}
    data['token'] = project.token
    data['text'] = 'test'
    data['title'] = 'testtitle'
    data['emails'] = ['test1@test.com', 'test2@test.com']

    response = client.post(url_for('api.alarm'),
                           headers=get_api_headers(),
                           data=json.dumps(data))
    assert response.status_code == 201

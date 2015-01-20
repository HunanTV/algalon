from urlparse import urlparse
from flask import request, Response, jsonify, current_app
from ..models import User, Project
from .. import db
from . import api


@api.route('/dsn/<username>/<project_name>/')
def register_dsn(username, project_name):
    user = User.query.filter_by(username=username).first_or_404()
    project = user.projects.filter_by(name=project_name).first()
    if project:
        token = project.token
    else:
        project = Project(name=project_name)
        user.projects.append(project)
        db.session.add(user)
        db.session.commit()
        token = project.token
    app = current_app
    url = app.config['ALGALON_SERVER_HOST']
    urlparts = urlparse(url)
    port = app.config['ALGALON_SERVER_PORT']
    token = project.token
    dsn = 'http://{token}@{host}:{port}{path}'.format(
        token=token,
        host=urlparts.hostname,
        port=port,
        path=urlparts.path)
    response = jsonify({'dsn': dsn})
    response.status_code = 201
    return response

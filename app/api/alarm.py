from flask import request, Response
from ..email import send_email
from .. import db
from ..models import Project, Alarm
from . import api
import json
import re

EMAIL_PATTERN = re.compile(
    r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$')


@api.route('/alarm/', methods=['POST'])
def alarm():
    data = request.get_json() or json.loads(request.data)
    if not data:
        return Response(status=400)

    token = data.get('token', '')
    text = data.get('text', '')
    title = data.get('title', '')
    emails = data.get('emails', None)
    if emails is None:
        emails = []
    additional_to_email = [x for x in emails if EMAIL_PATTERN.match(x)]

    project = Project.query.filter_by(token=token).first_or_404()
    to_email = map(lambda x: x.address, project.to_emails.all())
    to = list(set(to_email + additional_to_email))

    send_email(to, (project.name + ': ' + title).title(), 'mail/alarm',
               message=text)

    alarm = Alarm(text=text, title=title, recipients=', '.join(to))
    project.alarms.append(alarm)
    db.session.add(project)
    db.session.commit()
    return Response(status=201)

import hashlib
import uuid
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from . import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    is_admin = db.Column(db.Boolean(), default=False)
    projects = db.relationship('Project',
                               backref=db.backref('owner', lazy='joined'),
                               cascade='all, delete, delete-orphan',
                               lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email == current_app.config.get('ALGALON_ADMIN', ''):
                self.is_admin = True
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    @classmethod
    def get_or_create(cls, username, email):
        u = db.session.query(cls).filter(cls.username == username).first()
        if u:
            return u
        u = cls(username=username, email=email)
        db.session.add(u)
        db.session.commit()
        return u

    def is_administrator(self):
        return self.is_admin

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def __repr__(self):
        return '<User %r>' % self.username


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow())
    token = db.Column(db.String(64), unique=True, index=True, default=lambda: uuid.uuid4().hex)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    alarms = db.relationship('Alarm', backref='app', lazy='dynamic')
    to_emails = db.relationship('ToEmail',
                                backref=db.backref('project', lazy='joined'),
                                cascade='all, delete, delete-orphan',
                                lazy='dynamic')

    def reset_token(self):
        self.token = uuid.uuid4().hex
        db.session.add(self)
        return True


class Alarm(db.Model):
    __tablename__ = 'alarms'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32))
    text = db.Column(db.Text)
    recipients = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default=datetime.utcnow())
    app_id = db.Column(db.Integer, db.ForeignKey('projects.id'))


class ToEmail(db.Model):
    __tablename__ = 'to_emails'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(64),  nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    date_added = db.Column(db.DateTime, default=datetime.utcnow())

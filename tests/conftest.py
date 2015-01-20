from app import create_app
from app import db as _db
from app.models import User, Project
import pytest


@pytest.fixture(scope='session')
def app(request):
    app = create_app('testing')
    return app


@pytest.fixture(scope='module')
def db(app, request):
    _db.app = app
    _db.create_all()

    def teardown():
        _db.session.remove()
        _db.drop_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    connection = db.engine.connect()

    options = dict(bind=connection)
    session = db.create_scoped_session(options=options)
    transaction = connection.begin()

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session

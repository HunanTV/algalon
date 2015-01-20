from functools import wraps
from flask import abort, g, flash, url_for, redirect


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user and g.user.username == kwargs['username']:
            return f(*args, **kwargs)
        if g.user and g.user.username != kwargs['username']:
            return abort(403)
        flash('please login')
        return redirect(url_for('main.index'))

    return decorated_function

# coding: utf-8

import os
import json
import hmac
import tempfile
from urllib import urlencode
from urlparse import urljoin

from flask import request, redirect, current_app, _app_ctx_stack
from openid.extensions import sreg
from openid.consumer.consumer import Consumer, SUCCESS
from openid.store.filestore import FileOpenIDStore

sreg.data_fields = {
    'username': 'test',
    'email': 'test@xxx.com',
    'groups': '[]',
    'uid': '0'
}


def sign(user_cookie_name, user):
    s = user_cookie_name + user
    return hmac.new('123', s).hexdigest()


class OpenIDRouteNotFoundError(Exception):
    pass


class OpenID2User(dict):

    def __getattr__(self, name):
        return self.get(name, None)


class OpenID2Client(object):

    def __init__(self, verify_url, store):
        self.verify_url = verify_url
        self.store = store

    def login(self, req):
        continue_url = req.values.get('continue') or req.headers.get('Referer', '/')
        consumer = Consumer({}, self.store)
        authreq = consumer.begin(current_app.config['OPENID2_YADIS'])

        sregreq = sreg.SRegRequest(optional=['username', 'uid'],
                                   required=['email', 'groups'])
        authreq.addExtension(sregreq)

        verify_url = urljoin(req.host_url, self.verify_url) + '?' + urlencode({'continue': continue_url})
        urlencode({'continue': continue_url})
        url = authreq.redirectURL(return_to=verify_url, realm=req.host_url)
        return redirect(location=url)

    def verify(self, req):
        consumer = Consumer({}, self.store)
        return_to = req.values.get('continue', '/')
        authres = consumer.complete(req.args, urljoin(req.host_url, self.verify_url))
        res = redirect(location=return_to)
        if authres.status is SUCCESS:
            sregres = sreg.SRegResponse.fromSuccessResponse(authres)
            user = json.dumps({'openid': authres.identity_url})
            sig = sign(current_app.config['OPENID2_USER_COOKIE_NAME'], user=user)
            one_year = 3600 * 24 * 365
            res.set_cookie(current_app.config['OPENID2_USER_COOKIE_NAME'], user, max_age=one_year)
            res.set_cookie(current_app.config['OPENID2_SIG_COOKIE_NAME'], sig, max_age=one_year)
            profile = sregres and {s[0]: s[1] for s in sregres.items()} or {}
            res.set_cookie(current_app.config['OPENID2_PROFILE_COOKIE_NAME'], json.dumps(profile), max_age=one_year)
        return res

    def logout(self, req):
        continue_url = req.values.get('continue') or req.headers.get('Referer', '/')
        this_url = urljoin(req.host_url, continue_url)
        openid2_logout_url = current_app.config['OPENID2_LOGOUT'] + '?next=%s' % this_url
        res = redirect(location=openid2_logout_url)
        res.delete_cookie(current_app.config['OPENID2_USER_COOKIE_NAME'])
        res.delete_cookie(current_app.config['OPENID2_PROFILE_COOKIE_NAME'])
        res.delete_cookie(current_app.config['OPENID2_SIG_COOKIE_NAME'])
        return res


class OpenID2(object):

    def __init__(self, name='openid2',
                 file_store_path='',
                 app=None,
                 login_url='/login/',
                 verify_url='/login/verify/',
                 logout_url='/login/logout/',
                 openid2_yadis_url='',
                 openid2_logout_url='',
                 openid2_user_cookie_name='USER_COOKIE_NAME',
                 openid2_sig_cookie_name='SIG_COOKIE_NAME',
                 openid2_profile_cookie_name='PROFILE_COOKIE_NAME'):

        self.name = name
        if not file_store_path:
            file_store_path = os.path.join(tempfile.gettempdir(), 'algalon-openid2')
        self.file_store_path = file_store_path
        self.app = app

        self.login_url = login_url
        self.verify_url = verify_url
        self.logout_url = logout_url

        self.openid2_yadis_url = openid2_yadis_url
        self.openid2_logout_url = openid2_logout_url
        self.openid2_user_cookie_name = openid2_user_cookie_name
        self.openid2_sig_cookie_name = openid2_sig_cookie_name
        self.openid2_profile_cookie_name = openid2_profile_cookie_name

        self.store = FileOpenIDStore(self.file_store_path)

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('OPENID2_YADIS', self.openid2_yadis_url)
        app.config.setdefault('OPENID2_LOGOUT', self.openid2_logout_url)
        app.config.setdefault('OPENID2_USER_COOKIE_NAME', self.openid2_user_cookie_name)
        app.config.setdefault('OPENID2_SIG_COOKIE_NAME', self.openid2_sig_cookie_name)
        app.config.setdefault('OPENID2_PROFILE_COOKIE_NAME', self.openid2_profile_cookie_name)
        self.register_openid_route(app)
        app.add_template_global(self, self.name)

    def register_openid_route(self, app):
        if not (self.login_url and self.logout_url and self.verify_url):
            raise OpenIDRouteNotFoundError()

        # @app.before_request
        # def get_login_info():
        #     g.user = OpenID2User(json.loads(request.cookies.get(self.openid2_profile_cookie_name, '{}')))

        @app.route(self.login_url)
        def openid2_login():
            return self.openid2.login(request)

        @app.route(self.verify_url)
        def openid2_verify():
            return self.openid2.verify(request)

        @app.route(self.logout_url)
        def openid2_logout():
            return self.openid2.logout(request)

    def init_openid2(self):
        return OpenID2Client(self.verify_url, self.store)

    @property
    def openid2(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'openid2'):
                ctx.openid2 = self.init_openid2()
            return ctx.openid2

    def __getattr__(self, name):
        return getattr(self.openid2, name)

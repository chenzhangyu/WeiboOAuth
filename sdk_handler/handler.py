# encoding=utf-8
__author__ = 'lance'

import uuid

import tornado.web
from tornado.options import options

from weibo import APIClient
from base import BaseHandler


client = APIClient(app_key=options.app_key, app_secret=options.app_secret,
                   redirect_uri=options.callback_url)


class OauthSDKHandler(BaseHandler):
    """
    Oauth handler using python sdk from weibo.
    """
    def get(self):
        code = self.get_argument("code", default=None)

        if not code:
            oauth_state = str(uuid.uuid4())
            self.set_secure_cookie("oauth_state", oauth_state)
            self.redirect(client.get_authorize_url(state=oauth_state, forcelogin="true"))
        else:
            if self.get_argument("state") != self.get_secure_cookie("oauth_state"):
                raise tornado.web.HTTPError(403)

            # get access_token
            r = client.request_access_token(code)

            # save access_token
            access_token, expires_in, uid = r.access_token, r.expires_in, r.uid
            self.set_secure_cookie("access_token", access_token)
            self.set_secure_cookie("expires_in", str(expires_in))
            self.set_secure_cookie("uid", str(uid))
            self.write(r)


class FetchUserInfoSDKHandler(BaseHandler):
    """
    Handler to get user info with weibo SDK
    """
    def get(self):
        access_token = self.get_secure_cookie("access_token")
        expires_in = self.get_secure_cookie("expires_in")
        uid = self.get_secure_cookie("uid")
        client.set_access_token(access_token, expires_in)
        result = client.users.show.get(uid=uid)
        self.write(result)

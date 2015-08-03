# encoding=utf-8
__author__ = 'lance'

import uuid
import time
import tornado.gen

from tornado.options import options
from tornado.httputil import url_concat
from tornado.httpclient import AsyncHTTPClient
from tornado.log import access_log as logger


from .oauth import WeiboOauth2Mixin
from base import BaseHandler


class OauthHandler(BaseHandler, WeiboOauth2Mixin):
    """
    Oauth handler using tornado.auth module.
    """

    @tornado.gen.coroutine
    def get(self):
        # redirect_uri handler
        if self.get_argument("code", False):
            # check state
            if self.get_argument("state") != self.get_secure_cookie("oauth_state"):
                raise tornado.web.HTTPError(403)
            # fetch access token
            user = yield self.get_authenticated_user(
                redirect_uri=options.callback_url,
                code=self.get_argument("code"))
            logger.debug("access_token %s" % user["access_token"])
            logger.debug("expires_in %s" % user["expires_in"])
            logger.debug("uid %s" % user["uid"])
            # save access_token, expires etc.
            self.set_secure_cookie("access_token", user["access_token"])
            self.set_secure_cookie("expires_time", str(user["expires_in"] + int(time.time())))
            self.set_secure_cookie("uid", user["uid"])
            self.write(str(user))
        # generate authorization url and redirect
        else:
            oauth_state = str(uuid.uuid4())
            logger.debug(oauth_state)
            # save state
            self.set_secure_cookie("oauth_state", oauth_state)
            # csrf, force login
            yield self.authorize_redirect(
                client_id=options.app_key,
                redirect_uri=options.callback_url,
                response_type="code",
                extra_params=dict(state=oauth_state, forcelogin="true")
            )


class FetchPersonalInfo(BaseHandler):

    @tornado.gen.coroutine
    def get(self):
        access_token = self.get_secure_cookie("access_token")
        expires = self.get_secure_cookie("expires_time")
        uid = self.get_secure_cookie("uid")
        # validate access_token
        if access_token and expires and uid and expires > int(time.time()):
            http_client = AsyncHTTPClient()
            # generate api url, fetch use info
            url = url_concat("https://api.weibo.com/2/users/show.json",
                             dict(access_token=access_token, uid=uid))
            response = yield http_client.fetch(url)
            logger.debug(response.body)
            self.write(str(response.body))
        else:
            raise tornado.web.HTTPError(403)

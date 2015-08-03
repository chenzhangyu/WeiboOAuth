# encoding=utf-8
import uuid
import time
import logging
import tornado.ioloop
import tornado.web
import tornado.options
import tornado.gen
import tornado.log

from setting import setting
from tornado.options import options, define
from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import url_concat
from tornado.log import access_log as logger

from oauth import WeiboOauth2Mixin
from weibo import APIClient


logger.setLevel(logging.DEBUG)


class BaseHandler(tornado.web.RequestHandler):
    pass


class MainHandler(BaseHandler):
    """
    Homepage for demo.

    Render a page which contains a link referring to "/oauth".
    """

    def get(self):
        # self.render("index.html", oauth_url=options.oauth_url)
        self.render("index.html", oauth_url="/oauth")


class OauthSDKHandler(BaseHandler):
    """
    Oauth handler using python sdk from weibo.
    """

    client = APIClient(app_key=options.app_key, app_secret=options.app_secret,
                       redirect_uri=options.callback_url)

    def get(self):
        code = self.get_argument("code", default=None)
        if not code:
            err_msg = self.get_argument("error_description", default=None)
            self.write("failed to login " + err_msg)
        else:
            # get access_token
            r = self.client.request_access_token(code)
            # save access_token
            access_token, expires_in, uid = r.access_token, r.expires_in, r.uid
            self.client.set_access_token(access_token, expires_in)
            # fetch user info by invoking api
            result = self.client.users.show.get(uid=uid)
            self.write(result)


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


if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/oauth", OauthHandler),
        (r"/user", FetchPersonalInfo),
    ], **setting)
    application.listen(options.port)
    tornado.options.parse_command_line()
    tornado.ioloop.IOLoop.current().start()

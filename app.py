# encoding=utf-8

import logging
import tornado.ioloop
import tornado.web
import tornado.options
import tornado.gen
import tornado.log

from setting import setting
from tornado.options import options, define
from tornado.log import access_log as logger
from base import BaseHandler

# tornado.auth implementation
from oauth_handler.handler import OauthHandler
from oauth_handler.handler import FetchPersonalInfo as UserInfoHandler

# SDK implementation
# from sdk_handler.handler import OauthSDKHandler as OauthHandler
# from sdk_handler.handler import FetchUserInfoSDKHandler as UserInfoHandler

logger.setLevel(logging.DEBUG)


class MainHandler(BaseHandler):
    """
    Homepage for demo.

    Render a page which contains a link referring to "/oauth_handler".
    """

    def get(self):
        # self.render("index.html", oauth_url=options.oauth_url)
        self.render("index.html", oauth_url="/oauth")

if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/oauth", OauthHandler),
        (r"/user", UserInfoHandler),
    ], **setting)
    application.listen(options.port)
    tornado.options.parse_command_line()
    tornado.ioloop.IOLoop.current().start()

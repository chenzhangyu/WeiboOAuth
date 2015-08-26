# encoding=utf-8
__author__ = 'lance'
import functools

import tornado.auth

from tornado import escape
from tornado.httpclient import AsyncHTTPClient
from tornado.options import options

import urllib as urllib_parse


class OauthError(Exception):
    pass


def _on_access_token(future, response):
    if response.error:
        future.set_exception(OauthError('Weibo auth error: %s' % str(response)))
        return

    args = escape.json_decode(response.body)
    future.set_result(args)


class WeiboOauth2Mixin(tornado.auth.OAuth2Mixin):

    _OAUTH_AUTHORIZE_URL = "https://api.weibo.com/oauth2/authorize"
    _OAUTH_ACCESS_TOKEN_URL = "https://api.weibo.com/oauth2/access_token"

    @tornado.auth._auth_return_future
    def get_authenticated_user(self, redirect_uri, code, callback):
        http_client = AsyncHTTPClient()
        body = urllib_parse.urlencode({
            "redirect_uri": redirect_uri,
            "code": code,
            "client_id": options.app_key,
            "client_secret": options.app_secret,
            "grant_type": "authorization_code"
        })
        http_client.fetch(self._OAUTH_ACCESS_TOKEN_URL,
                          functools.partial(_on_access_token, callback),
                          method="POST",
                          headers={'Content-Type': 'application/x-www-form-urlencoded'}, body=body)

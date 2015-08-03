# encoding=utf-8

from tornado.options import define

define("port", default="YOUR_PORT", type=int, help="Main port")
define("app_key", default="WEIBO_APP_ID", help="Weibo APP KEY")
define("app_secret", default="WEIBO_APP_SECRET", help="Weibo APP SECRET")
define("callback_url", default="YOU_CALLBACK_URI", help="Weibo CALLBACK URL")

setting = dict(debug=True, cookie_secret="my_secret")

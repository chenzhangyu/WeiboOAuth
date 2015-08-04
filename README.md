##WeiboOAuth-a demo for OAuth client communicating with weibo

使用tornado框架，实现第三方应用OAuth登录。
demo里有两种实现，一种采用tornado.auth模块，另一种采用微博的Python SDK。

###使用
安装requirements.txt中的依赖库。
根据需要修改settting_sample.py，并重命名为setting.py，
在app.py中导入合适的handler（默认是tornado.auth实现）即可。

###LINCENSE
MIT

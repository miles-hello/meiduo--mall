from django.shortcuts import render
from django.views import View
from django import http
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from meoduo_mall.utils.response_code import RETCODE


# Create your views here.

class QQurlView(View):
    def get(self, request):
        next_url = request.GET.get('next')
        # 创建工具对象
        qq_tool = OAuthQQ(
            settings.QQ_CLIENT_ID,
            settings.QQ_CLIENT_SECRET,
            settings.QQ_REDIRECT_URI,
            next_url,

        )
        # 生成授权地址
        login_url = qq_tool.get_qq_url()
        # 响应
        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'ok',
            'login_url': login_url
        })


class QQopenidView(View):
    # 获取openid
    def get(self, request):
        code = request.GET.get('code')
        next_url = request.GET.get('state')

        qq_tool = OAuthQQ(
            settings.QQ_CLIENT_ID,
            settings.QQ_CLIENT_SECRET,
            settings.QQ_REDIRECT_URI,
            next_url, )
        try:
            token = qq_tool.get_access_token(code)
            openid = qq_tool.get_open_id(token)
        except:
            openid = 0

        return http.HttpResponse(openid)

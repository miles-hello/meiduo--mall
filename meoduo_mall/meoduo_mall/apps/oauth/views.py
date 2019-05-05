from django.shortcuts import render
from django.views import View
from django import http

# Create your views here.

class QQurlView(View):
    def get(self,request):
        pass
    # 生成授权地址
class QQopenidView(View):
    # 获取openid
    def get(self,request):
        pass
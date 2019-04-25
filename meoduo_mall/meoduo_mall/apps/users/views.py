from django.shortcuts import render, redirect
from django.views import View
from django import http
from django.contrib.auth import login
import re
from .models import User


class RegisterView(View):
    def get(self, request):
        '''
        响应注册页面
        '''
        # 1.接收
        # 2.验证
        # 3.处理
        # 4.响应：展示注册页面
        return render(request, 'register.html')

    def post(self, request):
        '''
        创建用户对象，保存到表中
        '''
        # 1.接收
        user_name = request.POST.get('user_name')
        pwd = request.POST.get('pwd')
        cpwd = request.POST.get('cpwd')
        phone = request.POST.get('phone')
        allow = request.POST.get('allow')

        # 2.验证
        # 2.1非空
        if not all([user_name, pwd, cpwd, phone, allow]):
            return http.HttpResponseBadRequest('参数不完整')
        # 2.2用户名格式
        if not re.match('^[a-zA-Z0-9_-]{5,20}$', user_name):
            return http.HttpResponseBadRequest('请输入5-20个字符的用户名')
        # 2.3用户名是否存在
        if User.objects.filter(username=user_name).count() > 0:
            return http.HttpResponseBadRequest('用户名已存在')
        # 2.4密码格式
        if not re.match('^[0-9A-Za-z]{8,20}$', pwd):
            return http.HttpResponseBadRequest('请输入8-20位的密码')
        # 2.5两个密码是否一致
        if pwd != cpwd:
            return http.HttpResponseBadRequest('两个密码不一致')
        # 2.6手机号格式
        if not re.match('^1[345789]\d{9}$', phone):
            return http.HttpResponseBadRequest('手机号格式错误')
        # 2.7手机号是否存在
        if User.objects.filter(mobile=phone).count() > 0:
            return http.HttpResponseBadRequest('手机号已存在')
        # 2.8allow对应的是复选框checkbox，如果不选中，则在请求报文中不包含这个数据，在非空已经验证，不需要再验证

        # 3.处理
        # 3.1保存用户对象
        # 问题：直接将数据保存到表中，而此处的密码需要加密再保存
        # user = User.objects.create(username=user_name, password=pwd, mobile=phone)
        # 解决：使用认证模块提供的创建用户的方法
        user = User.objects.create_user(username=user_name, password=pwd, mobile=phone)

        # 3.2状态保持
        # request.session['user_id']=user.id
        login(request, user)

        # 4.响应
        return redirect('/')


class UsernameCheckView(View):
    def get(self, request, username):
        # 接收、验证：在路由规定中已经完成

        # 处理：查询用户名对应对象的个数
        count = User.objects.filter(username=username).count()

        # 响应：对应ajax请求，返回json数据
        return http.JsonResponse({
            'count': count
        })


class MobileCheckView(View):
    def get(self, request, mobile):
        # 处理
        count = User.objects.filter(mobile=mobile).count()

        # 响应
        return http.JsonResponse({
            'count': count
        })

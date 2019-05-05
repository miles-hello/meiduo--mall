from django.shortcuts import render, redirect
from django.views import View
from django import http
from django.contrib.auth import login,logout
import re
from .models import User
from django_redis import get_redis_connection
from django.contrib.auth import authenticate
from django.contrib.auth.mixins import LoginRequiredMixin

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
        sms_code_request = request.POST.get('msg_code')

        # 2.验证
        # 2.1非空
        if not all([user_name, pwd, cpwd, phone, allow,sms_code_request]):
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
        redis_cli = get_redis_connection("verify_code")
        sms_code_redis = redis_cli.get('sms_' + phone)
        if sms_code_redis is None:
            return http.HttpResponseBadRequest('短信验证码过期')
        if sms_code_redis.decode()!=sms_code_request:
            return http.HttpResponseBadRequest('短信验证码错误')
        redis_cli.delete('sms_'+phone)
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

class LoginView(View):
    def get(self, request):
        return render(request,'login.html')

    def post(self, request):
        # 接收
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        next_url = request.GET.get('next','/')

        # 验证
        # 2.1非空
        if not all([username, pwd]):
            return http.HttpResponseBadRequest('参数不完整')
        # 2.2用户名格式
        if not re.match('^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseBadRequest('请输入5-20个字符的用户名')
        # 2.3密码格式
        if not re.match('^[0-9A-Za-z]{8,20}$', pwd):
            return http.HttpResponseBadRequest('请输入8-20位的密码')

        # 处理：查询，状态保持
        user = authenticate(username=username, password=pwd)
        if user is None:
            # 用户名或密码错误
            return render(request, 'login.html', {
                'loginerror': '用户名或密码错误'
            })
        else:
            # 用户名或密码正确，则状态保持，重定向
            login(request, user)
            # 输出cookie，用于前端提示
            response=redirect(next_url)
            response.set_cookie('username',user.username,max_age=60*60*24*14)
            return response

            # 响应

class LogoutView(View):
    def get(self,request):
        logout(request)
        response = redirect('/')
        response.delete_cookie('username')
        return response

class InfoView(LoginRequiredMixin,View):
    def get(self,request):
        # if not request.user.is_authenticated:
        #     return redirect('/')
        return render(request,'user_center_info.html')
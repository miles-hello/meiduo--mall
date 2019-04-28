from django.shortcuts import render
from django.views import View
from meoduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
# Create your views here.
from . import constants
from django import http
from meoduo_mall.utils.response_code import RETCODE
import random
from meoduo_mall.libs.yuntongxun.sms import CCP
from celery_tasks.sms.tasks import send_sms
import time

class Imagecodeview(View):
    def get(self,request,uuid):
        text,code,image = captcha.generate_captcha()


        redis_cli=get_redis_connection("verify_code")
        redis_cli.setex(uuid,constants.IMAGE_CODE_EXPIRES,code)

        return http.HttpResponse(image,content_type='image/png')

class SmscodeView(View):
    def get(self,request,mobile):
        # 接收
        image_code_request = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        # 验证
        redis_cli = get_redis_connection("verify_code")
        image_code_redis = redis_cli.get(uuid)
        if image_code_redis is None:
            return http.JsonResponse({
                'code':RETCODE.IMAGECODEERR,
                'errmsg':'图片验证码已经过期',

            })
        # 对比
        if image_code_redis.decode() != image_code_request.upper():
            return http.JsonResponse({
                'code': RETCODE.IMAGECODEERR,
                'errmsg': '图片验证码错误',
            })
        # 强制图形验证码
        redis_cli.delete(uuid)

        # 在60秒内只向指定手机号发一次短信
        if redis_cli.get('sms_flag_' + mobile):
            return http.JsonResponse({
                'code': RETCODE.SMSCODERR,
                'errmsg': '发送短信太频繁'
            })
            # 处理
            # 1.生成6位随机数
            sms_code = '%06d' % random.randint(0, 999999)

            # # 2.保存到redis中
            # redis_cli.setex('sms_' + mobile, constants.SMS_CODE_EXPIRES, sms_code)
            # # 是否在60秒内发送短信的标记
            # redis_cli.setex('sms_flag_' + mobile, constants.SMS_CODE_FLAG_EXPIRES, 1)

            # 优化redis：只与redis服务器交互一次
            redis_pl = redis_cli.pipeline()
            redis_pl.setex('sms_' + mobile, constants.SMS_CODE_EXPIRES, sms_code)
            redis_pl.setex('sms_flag_' + mobile, constants.SMS_CODE_FLAG_EXPIRES, 1)
            redis_pl.execute()

            # 3.发短信
            # time.sleep(5)
            # ccp = CCP()
            # ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_EXPIRES / 60], 1)
            # print(sms_code)
            # 调用任务
            send_sms.delay(mobile, [sms_code, constants.SMS_CODE_EXPIRES / 60], 1)

        # 响应

        return http.JsonResponse({
            'code':RETCODE.OK,
            'errmsg':"OK",

        })
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # 继承后，默认的属性、方法都有
    # 扩展新属性
    # 手机号
    mobile = models.CharField(max_length=11)

    class Meta:
        # 表名
        db_table = 'tb_users'

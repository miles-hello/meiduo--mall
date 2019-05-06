from django.db import models
from users.models import User
# Create your models here.
class OAuthQQUser(models.Model):
    user = models.ForeignKey(User)
    openid= models.CharField(max_length=50)

    class Meat:
        db_table= 'tb_oauth_qq'
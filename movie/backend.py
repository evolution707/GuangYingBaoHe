# -*- coding=utf-8 -*-

from django.contrib.auth.backends import ModelBackend
from .models import UserInfo


class EmailAuthBackend(ModelBackend):
    '''
    自定义验证email+password登录
    '''
    def authenticate(self, username=None, password=None):
        try:
            user = UserInfo.objects.get(email=username)
            if user.check_password(password):
                return user
            return None
        except UserInfo.DoesNotExist:
            return None
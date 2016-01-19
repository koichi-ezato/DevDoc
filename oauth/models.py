# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser


class OAuthUser(AbstractUser):
    """
    ユーザ認証に使用するユーザクラス
    """
    class Meta:
        verbose_name = u'ユーザ'
        verbose_name_plural = u'ユーザ'

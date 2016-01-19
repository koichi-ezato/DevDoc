# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import Top

urlpatterns = [
    url(r'^$', Top.as_view(), name='index'),
]

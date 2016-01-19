# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import Settings, List

urlpatterns = [
    url(r'^$', Settings.as_view(), name='index'),
    url(r'^list/', List.as_view(), name='list'),
]

# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import Render

urlpatterns = [
    url(r'^$', Render.as_view(), name='index'),
]

# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import Logout

urlpatterns = [
    url(r'^logout/', Logout.as_view(), name='logout'),
]

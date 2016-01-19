# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import Editor, AddNote

urlpatterns = [
    url(r'^$', Editor.as_view(), name='index'),
    url(r'^add/', AddNote.as_view(), name='add'),
]

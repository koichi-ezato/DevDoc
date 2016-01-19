# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import OAuthUser as User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

# -*- coding: utf-8 -*-
from django.views.generic import View
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


class Home(View):
    """
    HomeアプリケーションのViewクラス
    """
    template_name = 'home/index.html'

    @method_decorator(login_required)
    def get(self, request):
        """
        Home画面の表示
        :param request: リクエストデータ
        :return: レスポンスデータ
        """
        return render(request, self.template_name)

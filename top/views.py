# -*- coding: utf-8 -*-
from django.views.generic import View
from django.shortcuts import render


class Top(View):
    """
    TopアプリケーションのViewクラス
    ログインに失敗した場合もこのクラスへ遷移する
    アプリケーションの説明と利用開始ボタンがある画面
    """
    template_name = 'top/index.html'

    def get(self, request):
        """
        Top画面を表示する
        :param request: リクエストデータ
        :return: レスポンスデータ
        """
        return render(request, self.template_name)

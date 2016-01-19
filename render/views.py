# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


class Render(View):
    """
    RenderアプリケーションのViewクラス
    """
    @method_decorator(login_required)
    def get(self, request):
        """
        evernoteに貼ったリンクからこの機能が呼ばれる
        guidを取得して編集画面に遷移させる
        :param request: リクエストデータ
        :return: evernote編集画面へのリダイレクト
        """
        note_guid = request.GET.get('guid')

        if not note_guid:
            return redirect('settings:list')

        request.session['note_guid'] = note_guid

        return redirect('editor:index')

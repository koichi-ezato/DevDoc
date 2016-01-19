# -*- coding: utf-8 -*-
from pprint import pprint
from django.http import Http404
from evernote.api.client import EvernoteClient

from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from social.apps.django_app.default.models import UserSocialAuth
from django.conf import settings


class Logout(View):
    """
    ログアウト処理を行うクラス
    """
    @method_decorator(login_required)
    def get(self, request):
        """
        ログイン処理
        :param request: リクエストデータ
        :return: レスポンスデータ
        """
        logout(request)
        return redirect('top:index')


def get_token(username):
    """
    トークン取得
    :param username: ユーザID
    :return: トークン
    """
    user_social_auth = UserSocialAuth.objects.get(uid=username)
    token = user_social_auth.extra_data['access_token']['oauth_token']
    return token


def get_evernote_client(token=None):
    """
    evernoteクライアント取得
    :param token: トークン
    :return: evernoteクライアント
    """
    client = EvernoteClient(token=token, sandbox=settings.EVERNOTE_DEBUG)
    return client


def get_note_store(username):
    """
    note_store取得
    :param username: ユーザID
    :return: note_store
    """
    try:
        note_store = get_evernote_client(get_token(username)).get_note_store()
    except:
        raise Http404
    else:
        return note_store

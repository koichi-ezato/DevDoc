# -*- coding: utf-8 -*-
from django.contrib import messages
from django.views.generic import View
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import evernote.edam.notestore.ttypes as NoteStore
from .form import SettingForm
from oauth.views import get_note_store


class Settings(View):
    """
    SettingsアプリケーションのViewクラス
    Markdownで作成したノートの保存先となるノートブックを設定する
    """
    template_name = 'settings/index.html'

    @method_decorator(login_required)
    def get(self, request):
        notebook_guid = request.session.get('notebook_guid')
        form = SettingForm(
            user=request.user,
            initial={
                'notebook_guid': notebook_guid
            }
        )

        return render(request, self.template_name, {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = SettingForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():
            request.session['notebook_guid'] = \
                form.cleaned_data['notebook_guid']
            messages.success(request, u"設定保存しました")
            return redirect('settings:list')
        else:
            messages.error(request, u'設定保存に失敗しました')
            return render(request, self.template_name, {'form': form})


class List(View):
    template_name = 'settings/list.html'

    @method_decorator(login_required)
    def get(self, request):
        note_store = get_note_store(request.user.username)
        note_filter = NoteStore.NoteFilter()
        note_filter.words = 'contentClass:OSC.DevDoc'
        note_list = note_store.findNotes(note_filter, 0, 100)
        list = []
        for note in note_list.notes:
            notebook_info = note_store.getNotebook(
                note.notebookGuid, True, False, False, False)
            note_info = note_store.getNote(
                note.guid, True, False, False, False)
            list.append(
                {'notebook': notebook_info.name,
                 'guid': note_info.guid,
                 'title': note_info.title})
        return render(request, self.template_name, {'list': list})

    @method_decorator(login_required)
    def post(self, request):
        request.session['note_guid'] = request.POST.get('edit')
        return redirect('editor:index')

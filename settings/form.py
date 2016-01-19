# -*- coding: utf-8 -*-
from django import forms
from oauth.views import get_note_store


class SettingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(SettingForm, self).__init__(*args, **kwargs)

        note_store = get_note_store(self.user.username)
        notebooks = note_store.listNotebooks()
        note_book_guid_list = []
        for notebook in notebooks:
            note_book_guid_list.append([notebook.guid, notebook.name])

        self.fields['notebook_guid'] = forms.ChoiceField(
            choices=note_book_guid_list,
            widget=forms.Select(attrs={'class': 'form-control'},),
            label=u'Markdown保存用ノートブック'
        )

    def clean(self):
        cleaned_data = super(SettingForm, self).clean()
        return cleaned_data

    class Meta:
        fields = ('notebook_guid',)

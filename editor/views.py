# -*- coding: utf-8 -*-
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from oauth.views import get_note_store
from xml.etree.ElementTree import *
import evernote.edam.type.ttypes as types
import evernote.edam.error.ttypes as errors
from BeautifulSoup import BeautifulSoup
from django.conf import settings
import logging
logger = logging.getLogger()


class Editor(View):
    """
    EditorアプリケーションのViewクラス
    evernoteの編集を行う
    """
    template_name = 'editor/index.html'

    @method_decorator(login_required)
    def get(self, request):
        """
        evernote編集画面表示
        編集対象のevernoteを取得して
        画面に表示可能な状態にフォーマットする
        :param request: リクエストデータ
        :return: レスポンスデータ
        """
        note_guid = request.session.get('note_guid')

        if not note_guid:
            return redirect('settings:list')

        note_store = get_note_store(request.user.username)
        note = note_store.getNote(note_guid, True, False, False, False)

        root = fromstring(note.content)

        elem = root.find(u'center')

        resource = u""
        if elem is not None:
            resource = elem.text.replace('\n', '\r\n')

        return render(request, self.template_name, {'resource': resource})

    @method_decorator(login_required)
    def post(self, request):
        """
        evernote編集画面の保存処理
        postされたデータをENML形式に変換して保存する
        :param request: リクエストデータ
        :return: レスポンスデータ
        """
        title = request.POST.get('title')
        body = request.POST.get('body')
        resource = request.POST.get('resource')
        note_guid = request.session.get('note_guid')
        notebook_guid = request.session.get('notebook_guid')

        note_store = get_note_store(request.user.username)

        attrib = set_attributes()

        note = types.Note()
        if notebook_guid:
            note.notebookGuid = notebook_guid
        note.guid = note_guid
        note.title = make_title(title=title)

        soup = convert_enml(body=body)

        note.content = make_enml(guid=note.guid, soup=soup, resource=resource)

        note.attributes = attrib

        try:
            note = note_store.updateNote(note)
        except errors.EDAMUserException, edue:
            msg = u"EDAMUserException: " + str(edue).encode('utf-8')
            logger.error(msg=msg)
            messages.error(request, u'更新失敗')
        except errors.EDAMNotFoundException, ednfe:
            msg = u"EDAMNotFoundException: Invalid parent notebook GUID "
            msg += str(ednfe).encode('utf-8')
            logger.error(msg=msg)
            messages.error(request, u'更新失敗')
        else:
            request.session['note_guid'] = note.guid
            return redirect('editor:index')

        return redirect('settings:list')


class AddNote(View):
    """
    AddNoteクラスのViewアプリケーション
    evernoteの作成を行う
    """
    @method_decorator(login_required)
    def get(self, request):
        """
        evernote新規作成
        :param request: リクエストデータ
        :return: ノート一覧画面へのリダイレクト
        """
        notebook_guid = request.session.get('notebook_guid')
        if not notebook_guid:
            messages.info(request, u'保存先のノートブックを選択してください。')
            return redirect('settings:index')

        note_store = get_note_store(request.user.username)

        note = types.Note()
        note.notebookGuid = notebook_guid
        note.title = make_title()
        note.content = make_enml()
        note.attributes = set_attributes()

        try:
            note = note_store.createNote(note)
        except errors.EDAMUserException, edue:
            msg = u"EDAMUserException: " + str(edue).encode('utf-8')
            logger.error(msg=msg)
            messages.error(request, u'登録失敗')
        except errors.EDAMNotFoundException, ednfe:
            msg = u"EDAMNotFoundException: Invalid parent notebook GUID "
            msg += str(ednfe).encode('utf-8')
            logger.error(msg=msg)
            messages.error(request, u'登録失敗')
        else:
            request.session['note_guid'] = note.guid
            return redirect('editor:index')

        return redirect('settings:list')


def convert_enml(body):
    """
    Markdown表現のhtmlファイルをENML形式にコンバート
    ENMLは一般的なHTMLタグは使用可能だが、一部使用できないタグ、属性があるので
    この関数でコンバートを行う
    詳細は下記URLに記載されている
    https://dev.evernote.com/intl/jp/doc/articles/enml.php
    :param body: Markdown表現のHTMLデータ
    :return: ENMLに対応可能な状態にコンバートしたHTMLデータ
    """
    soup = BeautifulSoup(body)

    table = soup.findAll('table')
    th = soup.findAll('th')
    td = soup.findAll('td')

    # テーブルの整形処理
    for tbl in table:
        tbl['style'] = u'border-collapse: collapse; border-spacing: 0; ' \
                       u'margin-bottom: 20px;'

    for h in th:
        set_table_row_style(row=h, header=True)

    for d in td:
        set_table_row_style(row=d)

    # コードの整形処理(sunburst)
    code = soup.findAll('code')
    style = u'display: block;overflow-x: auto;padding: 0.5em;background: #000;color: #f8f8f8;'
    for c in code:
        code_class = c.get('class')
        if code_class is not None:
            if 'hljs' in code_class:
                c['style'] = style
                del c['class']
            else:
                del c['class']

    span = soup.findAll('span')
    for s in span:
        span_class = s.get('class')
        if span_class is not None:
            s['style'] = u''
            if 'hljs-comment' in span_class or 'hljs-quote' in span_class:
                s['style'] += u'color: #aeaeae;font-style: italic;'
            if 'hljs-keyword' in span_class \
                    or 'hljs-selector-tag' in span_class\
                    or 'hljs-type' in span_class:
                s['style'] += u'color: #e28964;'
            if 'hljs-string' in span_class:
                s['style'] += u'color: #65b042;'
            if 'hljs-subst' in span_class:
                s['style'] += u'color: #daefa3;'
            if 'hljs-regexp' in span_class or 'hljs-link' in span_class:
                s['style'] += u'color: #e9c062;'
            if 'hljs-title' in span_class or 'hljs-section' in span_class \
                    or 'hljs-tag' in span_class or 'hljs-name' in span_class:
                s['style'] += u'color: #89bdff;'
            if 'hljs-class' in span_class or 'hljs-title' in span_class \
                    or 'hljs-doctag' in span_class:
                s['style'] += u'text-decoration: underline;'
            if 'hljs-symbol' in span_class or 'hljs-bullet' in span_class\
                    or 'hljs-number' in span_class:
                s['style'] += u'color: #3387cc;'
            if 'hljs-params' in span_class or 'hljs-variable' in span_class\
                    or 'hljs-template-variable' in span_class:
                s['style'] += u'color: #3e87e3;'
            if 'hljs-attribute' in span_class:
                s['style'] += u'color: #cda869;'
            if 'hljs-meta' in span_class:
                s['style'] += u'color: #8996a8;'
            if 'hljs-formula' in span_class:
                s['style'] += u'background-color: #0e2231;color: #f8f8f8;font-style: italic;'
            if 'hljs-addition' in span_class:
                s['style'] += u'background-color: #253b22;color: #f8f8f8;'
            if 'hljs-deletion' in span_class:
                s['style'] += u'background-color: #420e09;color: #f8f8f8;'
            if 'hljs-selector-class' in span_class:
                s['style'] += u'color: #9b703f;'
            if 'hljs-selector-id' in span_class:
                s['style'] += u'color: #8b98ab;'
            if 'hljs-emphasis' in span_class:
                s['style'] += u'font-style: italic;'
            if 'hljs-strong' in span_class:
                s['style'] += u'font-weight: bold;'

            del s['class']
        else:
            del s['class']

    return soup


def set_table_row_style(row=None, header=False):
    """
    td,thタグのstyleをevernoteで表示するためのstyleを設定する
    :param row: tdもしくはthタグのデータ
    :param header: thの場合はTrue,それ以外はFalse
    :return: 変換後のtdもしくはthタグのデータ
    """
    # 共通的なスタイルを先に設定しておく
    style = u'padding: .5em;'
    style += u' '
    # thタグとtdタグではstyleがそれぞれ異なるので
    # th共通とtd共通のstyleを設定する
    if header:
        style += u'font-weight: bold; vertical-align: bottom; '
        style += u'border-top: 0;'
    else:
        style += u'vertical-align: top; '
        style += u'border-top: 1px solid #ddd;'

    # styleが設定されていない場合がある
    align = row.get('style')
    if align is not None:
        style += u' '
        if 'text-align:left' in align:
            style += u'text-align:left;'
        elif 'text-align:center' in align:
            style += u'text-align:center;'
        elif 'text-align:right' in align:
            style += u'text-align:right;'

    style += u' '
    style += u'border: 1px solid #ddd;'

    row['style'] = style


def make_title(title=None):
    """
    ノートのタイトルを設定する
    ユーザがタイトルを設定していない場合はこちらでタイトルを設定する
    :param title:
    :return:
    """
    if not title:
        title = u"名称未設定"
    return title.encode('utf-8')


def set_attributes():
    """
    evernoteのノートがDevDocで作成されたことがわかるように
    属性情報を設定する
    この属性情報はノート検索の時のフィルタとなる
    :return: evernoteの属性情報
    """
    attrib = types.NoteAttributes()
    attrib.sourceApplication = settings.EN_SOURCE_APP
    attrib.source = settings.EN_SOURCE
    attrib.contentClass = settings.EN_CONTENT_CLASS
    return attrib


def make_enml(guid=None, soup=None, resource=None):
    """
    enml形式のノート作成
    decode,encodeはこの関数内で処理する
    :param guid: noteのguid
    :param soup: パース済みのhtml形式のデータ
    :param resource: markdown形式のベースとなるデータ
    :return: enml形式のノート
    """
    xml_header = u"<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    enml_header = u"<!DOCTYPE en-note SYSTEM " \
                  u"\"http://xml.evernote.com/pub/enml2.dtd\">"
    note_tag = u"<en-note>"
    note_tag_end = u"</en-note>"
    if guid is not None:
        # guidがあればノートにつけるラベルを生成する
        if settings.DEBUG:
            href = settings.LINK_EVERNOTE_DEV
        else:
            href = settings.LINK_EVERNOTE_PRODUCT
        href += guid
        label = u"<del style='position:relative;display:block;'>"
        label += u"<a style='position: absolute;color: #FFF;" \
                 u"text-decoration: none;font-size: 12px;" \
                 u"height: 25px;border-radius: 0;margin-top: -20px;" \
                 u"right: 15px;background: rgba(0, 0, 0, 0);" \
                 u"border-left: 10px solid #BB3A34;" \
                 u"border-right: 10px solid #BB3A34;" \
                 u"border-bottom: 5px solid rgba(0, 0, 0, 0);width: 0;" \
                 u"text-indent:-100000px;' " \
                 u"href='"
        label += href
        label += u"'>Edit</a>"
        label += u"</del>"
    else:
        label = u""

    if soup is not None:
        # 変換しないとevernoteに登録できない
        unicode_soup = unicode(soup)
    else:
        unicode_soup = u""

    if resource is not None:
        # オリジナルのデータはノートの最後に隠し持っておく
        # ノートを開く時はここのデータを抽出している
        original_note = u"<div style='line-height: 1.6;font-size: 12px;'>"
        original_note += u"</div>"
        original_note += u"<center style='display:none;'>"
        original_note += resource
        original_note += u"</center><br/>"
    else:
        original_note = u""

    content = xml_header
    content += enml_header
    content += note_tag
    content += label
    content += unicode_soup
    content += original_note
    content += note_tag_end

    return content.encode('utf-8')

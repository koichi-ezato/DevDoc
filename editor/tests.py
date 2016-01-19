# -*- coding: utf-8 -*-
from pprint import pprint
from django.test import TestCase
from django.test import Client
from oauth.models import OAuthUser as User
from social.apps.django_app.default.models import UserSocialAuth
from BeautifulSoup import BeautifulSoup


class EditorViewTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='596560',
                                        email='koichi-ezato@osc-corp.co.jp',
                                        password='koichi-ezato')
        user_social_auth = UserSocialAuth()
        user_social_auth.provider = 'evernote-sandbox'
        user_social_auth.uid = '596560'
        user_social_auth.extra_data = '{"access_token": {"edam_webApiUrlPrefix": "https://sandbox.evernote.com/shard/s1/", "edam_shard": "s1", "oauth_token": "S=s1:U=91a50:E=158f7ee9efa:C=151a03d7140:P=185:A=koichi-ezato-3816:V=2:H=1a4e5efcc8f63951e17852d0c8019cab", "edam_expires": "1481628360442", "edam_userId": "596560", "edam_noteStoreUrl": "https://sandbox.evernote.com/shard/s1/notestore"}, "expires": 1481628360, "store_url": "https://sandbox.evernote.com/shard/s1/notestore", "oauth_token": "S=s1:U=91a50:E=158f7ee9efa:C=151a03d7140:P=185:A=koichi-ezato-3816:V=2:H=1a4e5efcc8f63951e17852d0c8019cab"}'
        user_social_auth.user = user
        user_social_auth.save()

        User.objects.create_user(username='000000',
                                 email='test@osc-corp.co.jp',
                                 password='000000')

        self.client = Client()
        self.client.login(username='596560', password='koichi-ezato')

    def test_index(self):
        response = self.client.get(path='/editor/')
        self.assertRedirects(response=response, expected_url='/settings/list/')

        session = self.client.session
        session['note_guid'] = '8b1dbb7b-4dd2-49be-b7e7-e323e9399fd9'
        session.save()
        response = self.client.get(path='/editor/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['resource'] is not None)

        session['note_guid'] = '2f7b4012-70e2-4d0f-9f5c-2ca468b2484e'
        session.save()
        response = self.client.get(path='/editor/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['resource'] is u'')

    def test_index_post(self):
        session = self.client.session
        session['note_guid'] = '8b1dbb7b-4dd2-49be-b7e7-e323e9399fd9'
        session.save()
        data = {
            'title': u"title",
            'body': u"<h1>title</h1>\n<hr/>\n<h2>sample</h2>\n<hr/>",
            'resource': u"# title\n-------\n## sample\n-------",
        }
        response = self.client.post(path='/editor/', data=data, follow=True)
        self.assertRedirects(response, expected_url='/editor/')

        session = self.client.session
        session['notebook_guid'] = 'b8f66bdc-f6ac-4194-a44d-cb39dcbf0142'
        session['note_guid'] = '8b1dbb7b-4dd2-49be-b7e7-e323e9399fd9'
        session.save()
        data = {
            'title': u"title",
            'body': u"<h1>title</h1>\n<hr/>\n<h2>sample</h2>\n<hr/>",
            'resource': u"# title\n-------\n## sample\n-------",
        }
        response = self.client.post(path='/editor/', data=data, follow=True)
        self.assertRedirects(response, expected_url='/editor/')

        session = self.client.session
        session['notebook_guid'] = 'b8f66bdc-f6ac-4194-a44d-cb39dcbf0142'
        session['note_guid'] = '8b1dbb7b-4dd2-49be-b7e7-e323e9399fd9'
        session.save()
        data = {
            'title': u"title",
            'body': u"<h1>title</h1>\n<hr/>\n<h2>sample</h2>\n<hr/><input type='text' />",
            'resource': u"# title\n-------\n## sample\n-------",
        }
        response = self.client.post(path='/editor/', data=data, follow=True)
        self.assertRedirects(response=response, expected_url='/settings/list/')
        self.assertContains(response=response, text=u"更新失敗", status_code=200)

        session = self.client.session
        session['notebook_guid'] = '000000000000000000000000000000000000'
        session['note_guid'] = '8b1dbb7b-4dd2-49be-b7e7-e323e9399fd9'
        session.save()
        data = {
            'title': u"title",
            'body': u"<h1>title</h1>\n<hr/>\n<h2>sample</h2>\n<hr/>",
            'resource': u"# title\n-------\n## sample\n-------",
        }
        response = self.client.post(path='/editor/', data=data, follow=True)
        self.assertRedirects(response=response, expected_url='/settings/list/')
        self.assertContains(response=response, text=u"更新失敗", status_code=200)

    def test_add(self):
        response = self.client.get(path='/editor/add/', follow=True)
        self.assertRedirects(response=response, expected_url='/settings/')
        self.assertContains(response=response, text=u"保存先のノートブックを選択してください。", status_code=200)

        session = self.client.session
        session['notebook_guid'] = 'b8f66bdc-f6ac-4194-a44d-cb39dcbf0142'
        session.save()
        response = self.client.get(path='/editor/add/', follow=True)
        self.assertRedirects(response=response, expected_url='/editor/')
        self.assertTrue(self.client.session['note_guid'] is not None)

        session = self.client.session
        session['notebook_guid'] = '000000000000000000000000000000000000'
        session.save()
        response = self.client.get(path='/editor/add/', follow=True)
        self.assertRedirects(response=response, expected_url='/settings/list/')
        self.assertContains(response=response, text=u"登録失敗", status_code=200)

    def test_convert_enml(self):
        from editor.views import convert_enml
        body = u'<table><thead><tr>'
        body += u'<th style="text-align:left">Left</th><th style="text-align:center">Center</th><th style="text-align:right">Right</th><th>Normal</th>'
        body += u'</tr></thead><tbody>'
        body += u'<td style="text-align:left">Left</td><td style="text-align:center">Center</td><td style="text-align:right">Right</td><td>Normal</td>'
        body += u'</tbody></table>'

        soup = convert_enml(body=body)

        expected = u'<table style="border-collapse: collapse; border-spacing: 0; margin-bottom: 20px;"><thead><tr>'
        expected += u'<th style="padding: .5em; font-weight: bold; vertical-align: bottom; border-top: 0; text-align:left; border: 1px solid #ddd;">Left</th>'
        expected += u'<th style="padding: .5em; font-weight: bold; vertical-align: bottom; border-top: 0; border: text-align:center; 1px solid #ddd;">Center</th>'
        expected += u'<th style="padding: .5em; font-weight: bold; vertical-align: bottom; border-top: 0; text-align:right; border: 1px solid #ddd;">Right</th>'
        expected += u'<th style="padding: .5em; font-weight: bold; vertical-align: bottom; border-top: 0; border: 1px solid #ddd;">Normal</th>'
        expected += u'</tr></thead><tbody>'
        expected += u'<td style="padding: .5em; vertical-align: top; border-top: 1px solid #ddd; text-align:left; border: 1px solid #ddd;">Left</td>'
        expected += u'<td style="padding: .5em; vertical-align: top; border-top: 1px solid #ddd; text-align:center; border: 1px solid #ddd;">Center</td>'
        expected += u'<td style="padding: .5em; vertical-align: top; border-top: 1px solid #ddd; text-align:right; border: 1px solid #ddd;">Right</td>'
        expected += u'<td style="padding: .5em; vertical-align: top; border-top: 1px solid #ddd; border: 1px solid #ddd;">Normal</td>'
        expected += u'</tbody></table>'
        expected_soup = BeautifulSoup(expected)
        self.assertEqual(soup, expected_soup)

    def test_make_title(self):
        from editor.views import make_title
        result = make_title()
        self.assertEqual(result, u"名称未設定".encode('utf-8'))

        title = u"タイトル"
        result = make_title(title=title)
        self.assertEqual(result, title.encode('utf-8'))

    def test_set_attributes(self):
        from editor.views import set_attributes
        import evernote.edam.type.ttypes as types
        expected = types.NoteAttributes()
        expected.sourceApplication = 'OSC_DevDoc'
        expected.source = 'OSC'
        expected.contentClass = 'OSC.DevDoc'
        result = set_attributes()
        self.assertEqual(result, expected)

    def test_make_enml(self):
        from editor.views import make_enml
        expected = u"<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        expected += u"<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
        expected += u"<en-note>"
        expected += u"</en-note>"

        result = make_enml()
        self.assertEqual(result, expected)

# -*- coding: utf-8 -*-
from pprint import pprint
from django.test import TestCase
from django.test import Client
from oauth.models import OAuthUser as User
from social.apps.django_app.default.models import UserSocialAuth


class SettingsViewTest(TestCase):
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

        self.client = Client()
        self.client.login(username='596560', password='koichi-ezato')

    def test_index(self):
        session = self.client.session
        session['notebook_guid'] = '299a5b39-d43a-404d-a8e5-2bf68ce33a72'
        session.save()
        response = self.client.get(path='/settings/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['form']['notebook_guid']) >= 0)

    def test_index_post(self):
        data = {
            'notebook_guid': '299a5b39-d43a-404d-a8e5-2bf68ce33a72'
        }
        response = self.client.post(path='/settings/', data=data, follow=True)
        self.assertRedirects(response=response, expected_url='/settings/list/')
        self.assertContains(response=response, text=u"設定保存しました", status_code=200)

        data = {
            'notebook_guid': ''
        }
        response = self.client.post(path='/settings/', data=data, follow=True)
        self.assertContains(response=response, text=u"設定保存に失敗しました", status_code=200)

    def test_list(self):
        response = self.client.get(path='/settings/list/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['list']) >= 0)

    def test_list_post(self):
        data = {
            'edit': '8b1dbb7b-4dd2-49be-b7e7-e323e9399fd9'
        }
        response = self.client.post(path='/settings/list/', data=data, follow=True)
        self.assertRedirects(response=response, expected_url='/editor/')
        self.assertEqual(self.client.session['note_guid'], '8b1dbb7b-4dd2-49be-b7e7-e323e9399fd9')

# -*- coding: utf-8 -*-
from pprint import pprint
from django.test import TestCase
from django.test import Client
from oauth.models import OAuthUser as User
from social.apps.django_app.default.models import UserSocialAuth


class OAuthViewTest(TestCase):
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

    def tearDown(self):
        User.objects.all().delete()
        UserSocialAuth.objects.all().delete()

    def test_logout(self):
        c = Client()
        c.login(username='596560', password='koichi-ezato')
        response = c.get('/oauth/logout/')
        # ログアウト後はTop画面へ遷移する
        self.assertRedirects(response, '/top/')
        # この状態でログインが必要な画面に遷移するとEvernoteのログイン画面が出ることを確認する
        response = c.get('/')
        self.assertRedirects(response=response, expected_url='/login/evernote-sandbox/?next=/', target_status_code=302)

    def test_get_token(self):
        from oauth.views import get_token
        token = get_token(username='596560')
        self.assertEqual(token, u"S=s1:U=91a50:E=158f7ee9efa:C=151a03d7140:P=185:A=koichi-ezato-3816:V=2:H=1a4e5efcc8f63951e17852d0c8019cab")

    def test_get_evernote_client(self):
        from oauth.views import get_token
        from oauth.views import get_evernote_client
        token = get_token(username='596560')
        client = get_evernote_client(token=token)
        self.assertEqual(client.token, u"S=s1:U=91a50:E=158f7ee9efa:C=151a03d7140:P=185:A=koichi-ezato-3816:V=2:H=1a4e5efcc8f63951e17852d0c8019cab")
        self.assertEqual(client.consumer_key, None)
        self.assertEqual(client.consumer_secret, None)
        self.assertEqual(client.additional_headers, {})
        self.assertEqual(client.sandbox, True)
        self.assertEqual(client.secret, None)
        self.assertEqual(client.service_host, 'sandbox.evernote.com')

    def test_get_note_store(self):
        from oauth.views import get_note_store
        note_store = get_note_store(username='596560')
        self.assertEqual(note_store.token, u"S=s1:U=91a50:E=158f7ee9efa:C=151a03d7140:P=185:A=koichi-ezato-3816:V=2:H=1a4e5efcc8f63951e17852d0c8019cab")
        self.assertEqual(note_store._user_agent_id, u"koichi-ezato-3816:V=2")

        client = Client()
        client.login(username='000000', password='000000')
        response = client.get('/settings/')
        self.assertEqual(response.status_code, 404)

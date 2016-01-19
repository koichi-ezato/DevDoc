# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test import Client
from oauth.models import OAuthUser as User
from social.apps.django_app.default.models import UserSocialAuth


class HomeViewTest(TestCase):
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

    def test_index(self):
        c = Client()
        c.login(username='596560', password='koichi-ezato')
        response = c.get('/')
        self.assertEqual(response.status_code, 200)

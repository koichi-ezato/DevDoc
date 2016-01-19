# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test import Client


class TopViewTest(TestCase):
    def test_index(self):
        c = Client()
        response = c.get('/top/')
        self.assertEqual(response.status_code, 200)

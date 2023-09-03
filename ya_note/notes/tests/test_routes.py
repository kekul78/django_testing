from http import HTTPStatus

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()
URL = {
    'home': 'notes:home',
    'login': 'users:login',
    'logout': 'users:logout',
    'signup': 'users:signup',
    'list': 'notes:list',
    'add': 'notes:add',
    'success': 'notes:success',
    'detail': 'notes:detail',
    'edit': 'notes:edit',
    'delite': 'notes:delete',
}


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_pages_availability_for_anonymous_user(self):
        urls = (
            (URL['home'], None),
            (URL['login'], None),
            (URL['logout'], None),
            (URL['signup'], None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = (
            (URL['list'], None),
            (URL['add'], None),
            (URL['success'], None),
        )
        for name, args in urls:
            self.client.force_login(self.author)
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        urls = (
            (URL['detail'], (self.note.slug,)),
            (URL['edit'], (self.note.slug,)),
            (URL['delite'], (self.note.slug,)),
        )
        users = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects(self):
        urls = (
            (URL['detail'], (self.note.slug,)),
            (URL['edit'], (self.note.slug,)),
            (URL['delite'], (self.note.slug,)),
            (URL['add'], None),
            (URL['success'], None),
            (URL['list'], None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                login_url = reverse(URL['login'])
                url = reverse(name, args=args)
                expected_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)

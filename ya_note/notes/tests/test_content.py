from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()
URL = {
    'add': 'notes:add',
    'list': 'notes:list',
    'edit': 'notes:edit',
}


class TestNoteContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Мимо Крокодил')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_notes_list_for_different_users(self):
        users = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for name, status in users:
            with self.subTest(name=name):
                url = reverse(URL['list'])
                response = name.get(url)
                object_list = response.context['object_list']
                self.assertIs((self.note in object_list), status)

    def test_pages_contains_form(self):
        urls = (
            (URL['add'], None),
            (URL['edit'], (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)

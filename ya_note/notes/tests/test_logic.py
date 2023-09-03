from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()
URL = {
    'add': 'notes:add',
    'edit': 'notes:edit',
    'delete': 'notes:delete',
    'success': 'notes:success',
    'login': 'users:login',
}


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Мимо Крокодил')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.url = reverse(URL['add'])
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_user_can_create_note(self):
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse(URL['success']))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.url, data=self.form_data)
        login_url = reverse(URL['login'])
        expected_url = f'{login_url}?next={self.url}'
        self.assertEqual(Note.objects.count(), 0)
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)


class TestNoteSlug(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Мимо Крокодил')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.url = reverse(URL['add'])
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse(URL['success']))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_not_unique_slug(self):
        note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=self.author,
        )
        self.form_data['slug'] = note.slug
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertFormError(response,
                             'form',
                             'slug',
                             errors=(note.slug + WARNING))


class TestNoteEditDelite(TestCase):

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
        cls.url = [reverse(URL['edit'], args=(cls.note.slug,)),
                   reverse(URL['delete'], args=(cls.note.slug,))]
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.url[0], self.form_data)
        self.assertRedirects(response, reverse(URL['success']))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        response = self.reader_client.post(self.url[0], self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        response = self.author_client.post(self.url[1])
        self.assertRedirects(response, reverse(URL['success']))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        response = self.reader_client.post(self.url[1])
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

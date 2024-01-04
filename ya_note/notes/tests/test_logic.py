from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestLogicCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.another_user = User.objects.create(username='Другой пользователь')
        cls.form_data = {'title': 'Заголовок', 'text': 'Текст'}

    def test_anon_cant_create_note(self):
        url = reverse('notes:add')
        self.client.post(url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_auth_client_create_note(self):
        url = reverse('notes:add')
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, 'Заголовок')
        self.assertEqual(note.text, 'Текст')
        self.assertEqual(note.author, self.author)

    def test_cant_create_two_same_slugs(self):
        url = reverse('notes:add')
        self.client.force_login(self.author)
        self.client.post(url, data=self.form_data)
        response = self.client.post(url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors='zagolovok - такой slug уже существует, '
            'придумайте уникальное значение!'
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_auto_complete_slug(self):
        url = reverse('notes:add')
        self.client.force_login(self.author)
        self.client.post(url, data=self.form_data)
        note = Note.objects.get()
        self.assertEqual(note.slug, 'zagolovok')


class TestLogicNoteAccess(TestCase):
    NOTE_TEXT = 'Текст'
    NEW_NOTE_TEXT = 'Редактирование'

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user = User.objects.create(username='Пользователь')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.note = Note.objects.create(title='Заголовок123',
                                       text=cls.NOTE_TEXT, author=cls.author)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.done_url = reverse('notes:success')
        cls.form_data = {'title': cls.note.title,
                         'text': cls.NEW_NOTE_TEXT,
                         'slug': cls.note.slug}

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.done_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note(self):
        response = self.user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.done_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note(self):
        response = self.user_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class SameTestData(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.another_user = User.objects.create(username='Обычный пользователь')
        cls.user_client = Client()
        cls.user_client.force_login(cls.another_user)


class TestContent(SameTestData):

    @classmethod
    def setUpTestData(cls):
        SameTestData.setUpTestData()
        cls.author_note = Note.objects.create(title='Заголовок1', text='Текст',
                                              author=cls.author)
        cls.another_user_note = Note.objects.create(title='Заголовок2',
                                                    text='Текст',
                                                    author=cls.another_user)

    def test_detail_in_list_context(self):
        url = reverse('notes:list')
        response = self.author_client.get(url)
        self.assertIn(self.author_note, response.context['object_list'])

    def test_another_notes_not_in_list(self):
        url = reverse('notes:list')
        response = self.author_client.get(url)
        self.assertNotIn(self.another_user_note,
                         response.context['object_list'])

    def test_form_in_add_and_edit(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.author_note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.tests.test_content import SameTestData


User = get_user_model()


class TestRoutes(SameTestData):

    @classmethod
    def setUpTestData(cls) -> None:
        SameTestData.setUpTestData()
        cls.note = Note.objects.create(title='Заголовок', text='Текст',
                                       author=cls.author)

    def test_home_page(self):
        urls = (
            ('notes:home', None),
            ('users:signup', None),
            ('users:login', None),
            ('users:logout', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirects_anonymous_client(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_auth_user_notes(self):
        urls = (
            'notes:list',
            'notes:success',
            'notes:add',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_detail_note_access(self):
        args = (self.note.slug,)
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.another_user, HTTPStatus.NOT_FOUND),
        )
        urls = ('notes:detail', 'notes:edit', 'notes:delete',)
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

import pytest

from pytest_django.asserts import assertFormError
from django.urls import reverse
from news.models import Comment
from news.forms import WARNING


@pytest.mark.django_db
@pytest.mark.parametrize(
    'param_user, expected_comments_count',
    (
        (pytest.lazy_fixture('client'), 0),
        (pytest.lazy_fixture('admin_client'), 1)
    )
)
def test_anon_cant_comment(param_user, comment_form_data, news,
                           expected_comments_count):
    url = reverse('news:detail', args=(news.pk,))
    param_user.post(url, data=comment_form_data)
    comments_count = Comment.objects.count()
    assert comments_count == expected_comments_count


@pytest.mark.django_db
def test_cant_use_bad_words(admin_client, news, bad_comment_form_data):
    url = reverse('news:detail', args=(news.pk,))
    response = admin_client.post(url, data=bad_comment_form_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_and_edit_comments(author_client, comment,
                                             edit_comment_form_data):
    url = reverse('news:edit', args=(comment.pk,))
    author_client.post(url, data=edit_comment_form_data)
    comment.refresh_from_db()
    assert comment.text == edit_comment_form_data['text']

    delete_url = reverse('news:delete', args=(comment.pk,))
    author_client.delete(delete_url)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_not_author_cant_delete_and_edit_comments(admin_client, comment,
                                                  edit_comment_form_data):
    url = reverse('news:edit', args=(comment.pk,))
    admin_client.post(url, data=edit_comment_form_data)
    comment.refresh_from_db()
    assert comment.text != edit_comment_form_data['text']

    delete_url = reverse('news:delete', args=(comment.pk,))
    admin_client.delete(delete_url)
    comments_count = Comment.objects.count()
    assert comments_count == 1

import pytest

from django.conf import settings
from django.urls import reverse


URL_HOME = reverse('news:home')


@pytest.mark.django_db
def test_homepage_news_quantity(client, news_creation):
    response = client.get(URL_HOME)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_homepage_news_date_sorted(client, news_creation):
    news_creation
    response = client.get(URL_HOME)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_datetime_sorted(client, comments_creation, news):
    comments_creation
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_dates = [comment.created for comment in all_comments]
    sorted_dates = sorted(all_dates)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_anon_has_no_form(client, news):
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_auth_has_form(admin_client, news):
    url = reverse('news:detail', args=(news.pk,))
    response = admin_client.get(url)
    assert 'form' in response.context

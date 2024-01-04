import pytest
from django.conf import settings
from django.utils import timezone
from news.models import News, Comment
from news.forms import BAD_WORDS
from datetime import datetime, timedelta


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def pk_for_news(news):
    return news.pk,


@pytest.fixture
def news_creation():
    today = datetime.today()
    News.objects.bulk_create(
        News(title=f'Новость {index}', text='Текст',
             date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comments_creation(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(news=news, author=author,
                                         text=f'Текст {index}')
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def comment_form_data(news, author):
    return {
        'news': news,
        'author': author,
        'text': 'Текст комментария'
    }


@pytest.fixture
def bad_comment_form_data(news, author):
    return {
        'news': news,
        'author': author,
        'text': f'Текст {BAD_WORDS[0]}'
    }


@pytest.fixture
def edit_comment_form_data(news, author):
    return {
        'news': news,
        'author': author,
        'text': 'Отредактированный текст'
    }

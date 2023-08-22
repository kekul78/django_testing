import pytest
from django.contrib.auth import get_user_model
from news.models import Comment, News
from datetime import date as dt
from datetime import datetime, timedelta
from django.conf import settings

User = get_user_model()


@pytest.fixture
def anonim(client):
    return client


@pytest.fixture
def form_data():
    return {
        'title': 'Заголовок',
        'text': 'Текст',
    }


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст',
        date=dt.today(),
        id=2,
    )


@pytest.fixture
def id_news(news):
    return news.id,


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        text='Текст комментария',
        author=author,
        created=dt.today(),
        news_id=news.id,
        id=2
    )


@pytest.fixture
def id_comment(comment):
    return comment.id,


@pytest.fixture
def news_count_on_homepage():
    today = datetime.today()
    all_news = [News(
                title=f'Новость {index}',
                text='Просто текст.',
                date=today - timedelta(days=index)
                )
                for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
                ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def many_comments(author, news):
    now = datetime.today()
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return comment

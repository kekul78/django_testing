import pytest
from django.urls import reverse
from django.conf import settings
from news.forms import CommentForm

HOME_URL = reverse('news:home')
URL = {
    'detail': 'news:detail'
}


@pytest.mark.django_db
def test_news_count(client, news_count_on_homepage):
    news_count_on_homepage
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_count_on_homepage):
    news_count_on_homepage
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        (URL['detail'], pytest.lazy_fixture('id_news')),
    ),
)
def test_comments_order(client, name, args, many_comments):
    detail_url = reverse(name, args=args)
    response = client.get(detail_url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    sorted_comments = all_comments.order_by('created',)
    for i in range(0, len(all_comments) - 2):
        assert sorted_comments[i].created < all_comments[i + 1].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, args, form_in_list',
    (
        (pytest.lazy_fixture('author_client'),
         pytest.lazy_fixture('id_news'), True),
        (pytest.lazy_fixture('anonim'),
         pytest.lazy_fixture('id_news'), False),
    )
)
def test_pages_contains_form(parametrized_client, args, form_in_list):
    url = reverse(URL['detail'], args=args)
    response = parametrized_client.get(url)
    form = response.context.get('form')
    assert (isinstance(form, CommentForm)) is form_in_list

import pytest
from django.urls import reverse
from django.conf import settings

HOME_URL = reverse('news:home')


@pytest.mark.django_db
def test_news_count(client, news_count_on_homepage):
    news_count_on_homepage
    response = client.get(HOME_URL)
    # Код ответа не проверяем, его уже проверили в тестах маршрутов.
    # Получаем список объектов из словаря контекста.
    object_list = response.context['object_list']
    # Определяем длину списка.
    news_count = len(object_list)
    # Проверяем, что на странице именно 10 новостей.
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_count_on_homepage):
    news_count_on_homepage
    response = client.get(HOME_URL)
    # Код ответа не проверяем, его уже проверили в тестах маршрутов.
    # Получаем список объектов из словаря контекста.
    object_list = response.context['object_list']
    # Получаем даты новостей в том порядке, как они выведены на странице.
    all_dates = [news.date for news in object_list]
    # Сортируем полученный список по убыванию.
    sorted_dates = sorted(all_dates, reverse=True)
    # Проверяем, что на странице именно 10 новостей.
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    # Предварительно оборачиваем имена фикстур
    # в вызов функции pytest.lazy_fixture().
    (
        ('news:detail',  pytest.lazy_fixture('id_news')),
    ),
)
def test_comments_order(client, name, args, many_comments):
    detail_url = reverse(name, args=args)
    response = client.get(detail_url)
    news = response.context['news']
    # Получаем все комментарии к новости.
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    # Задаём названия для параметров:
    'parametrized_client, args, form_in_list',
    (
        # Передаём фикстуры в параметры при помощи "ленивых фикстур":
        (pytest.lazy_fixture('author_client'),
         pytest.lazy_fixture('id_news'), True),
        (pytest.lazy_fixture('anonim'),
         pytest.lazy_fixture('id_news'), False),
    )
)
def test_pages_contains_form(parametrized_client, args, form_in_list):
    # Формируем URL.
    url = reverse('news:detail', args=args)
    # Запрашиваем нужную страницу:
    response = parametrized_client.get(url)
    # Проверяем, есть ли объект формы в словаре контекста:
    assert ('form' in response.context) is form_in_list

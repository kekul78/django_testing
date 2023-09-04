from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects
import pytest

URL = {
    'home': 'news:home',
    'login': 'users:login',
    'logout': 'users:logout',
    'signup': 'users:signup',
    'detail': 'news:detail',
    'edit': 'news:edit',
    'delite': 'news:delete',
}


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        (URL['home'], None),
        (URL['signup'], None),
        (URL['logout'], None),
        (URL['login'], None),
        (URL['detail'], pytest.lazy_fixture('id_news')),
    ),
)
def test_home_availability_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'name',
    (URL['edit'], URL['delite']),
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, expected_status, name, id_comment
):
    url = reverse(name, args=(id_comment))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        (URL['edit'], pytest.lazy_fixture('id_comment')),
        (URL['delite'], pytest.lazy_fixture('id_comment'))
    ),
)
def test_redirect_for_anonymous_client(client, name, args):
    login_url = reverse(URL['login'])
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)

from pytest_django.asserts import assertRedirects
from news.models import Comment
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from http import HTTPStatus

from news.models import Comment

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('id_news')),
    ),
)
def test_anonymous_user_cant_create_comment(client, form_data, name, args):
    url = reverse(name, args=args)
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('id_news')),
    ),
)
def test_user_can_create_comment(
        name, args, author_client, author, news
):
    form_data = {'text': 'Текст комментария'}
    url = reverse(name, args=args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = get_object_or_404(Comment)
    assert comment.news == news
    assert comment.text == 'Текст комментария'
    assert comment.author == author


def test_author_can_delete_comment(
        author_client, id_news, id_comment
):
    url = reverse('news:delete', args=(id_comment))
    response = author_client.delete(url)
    news_url = reverse('news:detail', args=(id_news))
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        id_comment, reader_client
):
    url = reverse('news:delete', args=(id_comment))
    response = reader_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        author_client, id_comment, id_news, comment
):
    form_data = {'text': 'Обновлённый комментарий'}
    url = reverse('news:edit', args=id_comment)
    response = author_client.post(url, data=form_data)
    news_url = reverse('news:detail', args=(id_news))
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == 'Обновлённый комментарий'


def test_user_cant_edit_comment_of_another_user(
        reader_client, id_comment, comment
):
    form_data = {'text': 'Обновлённый комментарий'}
    url = reverse('news:edit', args=id_comment)
    response = reader_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'

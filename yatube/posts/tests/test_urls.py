from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post, User

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_edit_redirect(self):
        """Страница /post_edit/ редерикт."""
        self.user_2 = User.objects.create_user(username='Ya')
        self.user_not_author = Client()
        self.user_not_author.force_login(self.user_2)
        response = self.user_not_author.get(f'/posts/{self.post.id}/edit/')
        self.assertRedirects(
            response, (f'/posts/{self.post.id}/'), HTTPStatus.FOUND)

    def test_home_url_exist(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_post_url_exist(self):
        """Страница group доступна любому пользователю."""
        response = self.guest_client.get(f'/group/{self.group.slug}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_url_exist(self):
        """Страница post доступна любому пользователю."""
        response = self.guest_client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_exist(self):
        """Страница profile доступна любому пользователю."""
        response = self.guest_client.get(f'/profile/{self.user.username}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url(self):
        """Страница /create/ доступна авторизованному пользователю"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url(self):
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_url(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_redirects_anonymous_on_admin_login(self):
        """Редирект неавторизованного пользователя"""
        test_redirect = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post.id}/edit/':
                f'/auth/login/?next=/posts/{self.post.id}/edit/'}
        for urls, redirect_url in test_redirect.items():
            with self.subTest(urls=urls):
                response = self.guest_client.get(urls)
                self.assertRedirects(response, redirect_url)

    def post_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/post_create_.html',
            f'/posts/{self.post.id}/edit/': 'posts/post_create_.html',
            '/error/': 'core/404.html'}
        for address, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

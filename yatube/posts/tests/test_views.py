from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.contrib.auth import get_user_model

from ..forms import PostForm
from ..models import Group, Post, User, Follow

TEST_OF_POST = 13
User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cache.clear()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image_name = 'small.gif'
        cls.uploaded = SimpleUploadedFile(
            name=cls.image_name,
            content=cls.small_gif,
            content_type='image/gif'
        )        
        cls.user = User.objects.create(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_tempate(self):
        """URL-адрес использует собственный шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.post.author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
            reverse("posts:post_create"): "posts/create_post.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_contex(self):
        """Шаблоны index, с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        db_first_post = Post.objects.first()
        self.assertEqual(first_object, db_first_post)

    def test_group_list_show_correct_contex(self):
        """Шаблоны group_list с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        db_first_group_post = Post.objects.filter(group=self.group).first()
        task_group = response.context['group']
        self.assertEqual(task_group, self.group)
        self.assertEqual(first_object, db_first_group_post)

    def test_profile_show_correct_contex(self):
        """Шаблоны profile с правильным контекстом."""
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': self.post.author})
        )
        first_object = response.context['page_obj'][0]
        db_first_group_post = Post.objects.filter(author=self.user).first()
        task_profile = response.context['author']
        self.assertEqual(task_profile, self.user)
        self.assertEqual(first_object, db_first_group_post)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').group, self.post.group)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным  контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным  контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}))
        is_edit_context = response.context.get('is_edit')
        self.assertTrue(is_edit_context)
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertEqual(response.context['form'].instance, self.post)

    def test_add_comment(self):
        """Авторизированный пользователь может оставить коментарий"""

        coments = {'text': 'тестовый комментарий'}
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=coments, follow=True
        )
        response = self.authorized_client.get(f'/posts/{self.post.id}/')
        self.assertContains(response, coments['text'])

    def test_anonym_cannot_add_comments(self):
        """НЕ Авторизированный пользователь не может оставить коментарий"""
        coments = {'text': 'комент не пройдет'}
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=coments, follow=True
        )
        response = self.guest_client.get(f'/posts/{self.post.id}/')
        self.assertNotContains(response, coments['text'])

    def test_cache_index(self):
        """Проверка хранения и очищения кэша для index."""
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            text='новый пост',
            author=self.post.author,
        )
        response_old = self.authorized_client.get(reverse('posts:index'))
        old_posts = response_old.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        response_new = self.authorized_client.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='test',
            slug='test',
        )
        Post.objects.bulk_create([
            Post(text=str(i), author=cls.user, group=cls.group)
            for i in range(1, 14)
        ])

    def setUp(self):
        self.guest_client = Client()
        cache.clear()

    def test_first_index_page_contains_ten_records(self):
        """Количество постов на первой странице ровно 10'"""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_index_page_contains_three_records(self):
        """Количество постов на второй странице ровно 3"""
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_group_page_contains_ten_records(self):
        """Количество постов на первой странице ровно 10"""
        url = reverse('posts:group_list', kwargs={'slug': self.group.slug})
        response = self.guest_client.get(url)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_group_page_contains_three_records(self):
        """Количество постов на второй странице ровно 3"""
        url = reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}) + '?page=2'
        response = self.guest_client.get(url)
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_profile_page_contains_ten_records(self):
        """Количество постов на первой странице ровно 10"""
        username = self.user.username
        url = reverse('posts:profile', kwargs={'username': username})
        response = self.guest_client.get(url)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_profile_page_contains_three_records(self):
        """Количество постов на второй странице ровно 3"""
        username = self.user.username
        page2 = '?page=2'
        url = reverse('posts:profile', kwargs={'username': username}) + page2
        response = self.guest_client.get(url)
        self.assertEqual(len(response.context['page_obj']), 3)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower1 = User.objects.create_user(username='author1')
        cls.follower2 = User.objects.create_user(username='author2')
        cls.follower3 = User.objects.create_user(username='author3')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.follower1)
        self.authorized_client3 = Client()
        self.authorized_client3.force_login(self.follower3)

    def test_follow(self):
        """Пользовтель может подписаться на автора."""
        self.authorized_client.post(reverse(
            'posts:profile_follow',
            kwargs={'username': self.follower2.username}))
        self.assertTrue(Follow.objects.filter(
            user=self.follower1,
            author=self.follower2).exists())

    def test_unfollow(self):
        """Пользовтель может отписаться от автора."""
        Follow.objects.create(
            user=self.follower1,
            author=self.follower2)
        self.authorized_client.post(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.follower2.username}))
        self.assertFalse(Follow.objects.filter(
            user=self.follower1,
            author=self.follower2).exists())

    def test_new_post_appears_subscribers_feed(self):
        """Запись будет на странице подписчика
        и не появится на странице не подписанного пользователя.
        """
        Follow.objects.create(
            user=self.follower1,
            author=self.follower2)
        post = Post.objects.create(
            author=self.follower2,
            text='Тестовый пост')
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(post, response.context['page_obj'])
        response = self.authorized_client3.get(reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page_obj'])

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает str."""
        posts = PostModelTest.post
        text_post = posts.text[:15]
        self.assertEqual(text_post[:15], str(posts))

    def test_models_have_correct_object_names1(self):
        object_group = PostModelTest.group
        group_title = object_group.title
        self.assertEqual(group_title, str(object_group.title))

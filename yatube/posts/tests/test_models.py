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
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает str."""
        post = PostModelTest.post
        expected_object_name = post.text
        self.assertEqual(expected_object_name[:15], str(post))
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_models_have_correct_object_names1(self):
        object_group = PostModelTest.group
        group_title = object_group.title
        self.assertEqual(group_title, str(object_group.title))

from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User
import time


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_name1',)
        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test_slug',
            description="Тестовое описание",)
        time.sleep(0.01)
        cls.group2 = Group.objects.create(
            title=('Заголовок для тестовой группы 2'),
            slug='test_slug2',
            description="Тестовое описание 2",)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись для создания нового поста',
            group=cls.group,)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create_form(self):
        """Проверка создания записи в БД."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Теcт добавления поста',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post_latest = Post.objects.latest('id')
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.post.author}))
        self.assertEqual(post_latest.text, form_data['text'])
        self.assertEqual(post_latest.group.id, form_data['group'])

    def test_post_edit_form(self):
        """Проверка редактирования записи в БД и смены группы."""
        posts_group_count = Post.objects.filter(
            group=PostPagesTests.group
        ).count()
        form_data = {
            'text': 'Теcт редактирования поста',
            'group': self.group2.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostPagesTests.post.id}),
            data=form_data,
            follow=True
        )
        post_latest = Post.objects.latest('id')
        self.assertEqual(Post.objects.filter(
            group=PostPagesTests.group).count(), posts_group_count - 1)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': PostPagesTests.post.id}))
        self.assertEqual(post_latest.text, form_data['text'])
        self.assertEqual(post_latest.group.id, form_data['group'])

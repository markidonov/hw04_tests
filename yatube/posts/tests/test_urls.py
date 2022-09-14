from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_name1',)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись для создания нового поста',)

        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test_slug',
            description="Тестовое описание",
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
# Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_index_group_profail(self):
        """Cтраницы: главная, группы, профиля,
        отдельно взятого поста - доступны всем.
        """
        url_names = (
            '/',
            '/group/test_slug/',
            '/profile/test_name1/',
            f'/posts/{self.post.id}/',
        )
        for address in url_names:
            with self.subTest():
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_create_for_authorized(self):
        """Страница /create доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_redirect_anonymous_on_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_post_edit_for_author(self):
        """Страница 'posts/<int:post_id>/edit/' доступна автору."""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/test_name1/': 'posts/profile.html',
            '/create/': 'posts/post_create.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/post_create.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(url=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_page_404(self):
        response = self.guest_client.get('/j7ytkuk6ybkjb87ku/')
        self.assertEqual(response.status_code, 404)

    # def test_private_url(self):
        #     """без авторизации приватные URL недоступны"""
        #     url_names = (
        #         '/create/',
        #         '/admin/',
        #     )
        #     for address in url_names:
        #         with self.subTest():
        #             response = self.guest_client.get(address)
        #             self.assertEqual(response.status_code, 302)

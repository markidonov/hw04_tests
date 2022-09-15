from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from http import HTTPStatus
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
        cls.index_url = '/'
        cls.group_url = '/group/test_slug/'
        cls.profail_url = '/profile/test_name1/'
        cls.post_detail_url = f'/posts/{cls.post.id}/'
        cls.create_url = '/create/'
        cls.edit_url = f'/posts/{cls.post.id}/edit/'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_group_profail(self):
        """Cтраницы: главная, группы, профиля,
        отдельно взятого поста - доступны всем.
        """
        task = TaskURLTests
        url_names = (
            task.index_url,
            task.group_url,
            task.profail_url,
            task.post_detail_url,
        )
        for address in url_names:
            with self.subTest():
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_for_authorized(self):
        """Страница /create доступна авторизованному пользователю."""
        response = self.authorized_client.get(TaskURLTests.create_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_anonymous_on_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get(TaskURLTests.create_url, follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_for_author(self):
        """Страница 'posts/<int:post_id>/edit/' доступна автору."""
        response = self.authorized_client.get(TaskURLTests.edit_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        task = TaskURLTests
        templates_url_names = {
            task.index_url: 'posts/index.html',
            task.group_url: 'posts/group_list.html',
            task.profail_url: 'posts/profile.html',
            task.create_url: 'posts/post_create.html',
            task.post_detail_url: 'posts/post_detail.html',
            task.edit_url: 'posts/post_create.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(url=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_page_404(self):
        response = self.guest_client.get('/any_wrong_address/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

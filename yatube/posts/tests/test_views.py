
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User
from posts.forms import PostForm
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
        time.sleep(0.01)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись для создания нового поста',
            group=cls.group,)
        time.sleep(0.01)
        cls.post2 = Post.objects.create(
            author=cls.user,
            text='Вторая тестовая запись для создания нового поста',
            group=cls.group2,)
        time.sleep(0.01)
        cls.post3 = Post.objects.create(
            author=cls.user,
            text='Третья тестовая запись для создания нового поста',)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.client = User.objects.create_user(username='Noname',)
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}):
                'posts/group_list.html',
            reverse('posts:profile', args={PostPagesTests.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id':
                    PostPagesTests.post.id}): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id':
                    PostPagesTests.post.id}): 'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        NUMBER_OF_POSTS = 3
        POST_PLACE = 2
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), NUMBER_OF_POSTS)
        first_object = response.context['page_obj'][POST_PLACE]
        test_author = first_object.author.username
        test_text = first_object.text
        self.assertEqual(test_author, PostPagesTests.user.username)
        self.assertEqual(test_text, PostPagesTests.post.text)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        POST_PLACE = 0
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug':
                                                PostPagesTests.group.slug}))
        first_object = response.context['page_obj'][POST_PLACE]
        test_text = first_object.text
        self.assertEqual(test_text, PostPagesTests.post.text)
        self.assertEqual(response.context['group'], PostPagesTests.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        POST_PLACE = 2
        response = self.authorized_client.get(
            reverse('posts:profile', args={PostPagesTests.user.username}))
        first_object = response.context['page_obj'][POST_PLACE]
        test_text = first_object.text
        self.assertEqual(test_text, PostPagesTests.post.text)
        self.assertEqual(response.context['author'].username,
                         PostPagesTests.user.username)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': PostPagesTests.post.id}))
        first_object = response.context['post']
        test_text = first_object.text
        self.assertEqual(test_text, PostPagesTests.post.text)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostPagesTests.post.id}))
        first_object = response.context['post']
        test_text = first_object.text
        self.assertEqual(test_text, PostPagesTests.post.text)

    def test_post_another_group(self):
        """Пост не попал в другую группу"""
        POST_PLACE = 0
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug':
                                                PostPagesTests.group2.slug}))
        first_object = response.context["page_obj"][POST_PLACE]
        test_text = first_object.text
        self.assertEqual(test_text, PostPagesTests.post2.text)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        form = PostForm(data={
            'text': 'Теcтовый текст',
            'group': self.group.id
        })
        self.assertTrue(form.is_valid())


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        POSTS_COUNT = 13
        cls.user = User.objects.create_user(username='test_name1',)
        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test_slug',
            description="Тестовое описание",)
        for x in range(POSTS_COUNT):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'{x}Тестовая запись нового поста',
                group=cls.group,)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.unathorized_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_index_first_page_contains_ten_records(self):
        response = self.unathorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_first_page_contains_ten_records(self):
        response = self.unathorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': PaginatorViewsTest.group.slug}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_second_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug':
                            PaginatorViewsTest.group.slug}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profail_first_page_contains_ten_records(self):
        response = self.unathorized_client.get(
            reverse('posts:profile',
                    args={PaginatorViewsTest.user.username}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profail_second_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:profile',
                    args={PaginatorViewsTest.user.username}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

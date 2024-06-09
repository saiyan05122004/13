from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, Comment

class PostCreationTest(TestCase):
    def setUp(self):
        # Создаем тестового пользователя и входим под ним
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

    def test_create_post(self):
        # Отправляем POST-запрос на создание поста
        response = self.client.post(reverse('home:post_create'), {
            'body': 'Это тестовый пост.'
        })
        # Проверяем, что запрос завершился перенаправлением (код 302)
        self.assertEqual(response.status_code, 302)
        # Проверяем, что пост был создан в базе данных
        self.assertTrue(Post.objects.filter(body='Это тестовый пост.').exists())

class CommentCreationTest(TestCase):
    def setUp(self):
        # Создаем тестового пользователя и пост
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.post = Post.objects.create(user=self.user, body='Это тестовый пост.')
        self.client.login(username='testuser', password='password123')
        # Создаем комментарий для тестирования ответов
        self.comment = Comment.objects.create(user=self.user, post=self.post, body='Тестовый комментарий')

    def test_create_comment(self):
        # Отправляем POST-запрос на создание комментария
        response = self.client.post(reverse('home:add_reply', kwargs={'post_id': self.post.pk, 'comment_id': self.comment.pk}), {
            'body': 'Это тестовый комментарий.'
        })
        # Проверяем, что запрос завершился перенаправлением (код 302)
        self.assertEqual(response.status_code, 302)
        # Проверяем, что комментарий был создан в базе данных
        self.assertTrue(Comment.objects.filter(body='Это тестовый комментарий.').exists())

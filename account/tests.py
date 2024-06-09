from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class UserRegistrationTest(TestCase):
    def test_registration(self):
        # Отправляем POST-запрос на регистрацию пользователя
        response = self.client.post(reverse('account:user_register'), {
            'username': 'testuser',
            'email': 'testuser@gmail.com',
            'password1': 'password123',
            'password2': 'password123'
        })
        # Проверяем, что запрос завершился перенаправлением (код 302)
        self.assertEqual(response.status_code, 302)
        # Проверяем, что пользователь был создан в базе данных
        self.assertTrue(User.objects.filter(username='testuser').exists())

class UserLoginTest(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_login(self):
        # Отправляем POST-запрос на вход пользователя
        response = self.client.post(reverse('account:user_login'), {
            'username': 'testuser',
            'password': 'password123'
        })
        # Проверяем, что запрос завершился перенаправлением (код 302)
        self.assertEqual(response.status_code, 302)
        # Проверяем, что пользователь был аутентифицирован
        self.assertTrue(response.wsgi_request.user.is_authenticated)

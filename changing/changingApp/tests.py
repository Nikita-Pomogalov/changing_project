from django.contrib.auth.forms import AuthenticationForm
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Announcement
from .forms import UserCreationForm, LoginForm, AnnouncementForm
from django.core.files.uploadedfile import SimpleUploadedFile
User = get_user_model()


class UserAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.test_user = {
            'username': 'testuser',
            'password1': 'Testpass123',
            'password2': 'Testpass123'
        }

    # Тесты регистрации
    def test_user_registration_view(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIsInstance(response.context['form'], UserCreationForm)

    def test_successful_user_registration(self):
        response = self.client.post(self.register_url, self.test_user, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertRedirects(response, reverse('main'))

    def test_password_mismatch_registration(self):
        data = self.test_user.copy()
        data['password2'] = 'Wrongpass123'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='testuser').exists())

    # Тесты авторизации
    def test_user_login_view(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertIsInstance(response.context['form'], AuthenticationForm)

    def test_successful_user_login(self):
        User.objects.create_user(username='testuser', password='Testpass123')
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'Testpass123'
        }, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, reverse('main'))

    def test_failed_user_login(self):
        response = self.client.post(self.login_url, {
            'username': 'nonexistent',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)


class FormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_login(self.user)

    def test_announcement_form_valid(self):
        form_data = {
            'title': 'Test Announcement',
            'description': 'Test description',
            'category': 'Test category',
            'condition': 'new'
        }
        form = AnnouncementForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_announcement_form_invalid(self):
        form_data = {
            'title': '',  # Пустое поле
            'description': 'Test description',
            'category': 'Test category',
            'condition': 'invalid'  # Неверный выбор
        }
        form = AnnouncementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)  # Ожидаем 2 ошибки
